from typing import Dict, Optional
import SLE_Model_Autofit as af
import SLE_Model_Autogalaxy as ag
from SLE_Model_Autogalaxy.SLE_Model_Analysis.SLE_Model_Analysis.analysis import (
    Analysis as AgAnalysis,
)
from SLE_Model_Autolens.SLE_Model_Analysis.SLE_Model_Analysis.lens import AnalysisLens
from SLE_Model_Autolens.SLE_Model_Analysis.plotter_interface import PlotterInterface
from SLE_Model_Autolens.SLE_Model_Point.SLE_Model_Fit.SLE_Model_Positions.abstract import (
    AbstractFitPositions,
)
from SLE_Model_Autolens.SLE_Model_Point.SLE_Model_Fit.SLE_Model_Positions.SLE_Model_Image.pair_repeat import (
    FitPositionsImagePairRepeat,
)
from SLE_Model_Autolens.SLE_Model_Point.SLE_Model_Fit.dataset import FitPointDataset
from SLE_Model_Autolens.SLE_Model_Point.dataset import PointDataset
from SLE_Model_Autolens.SLE_Model_Point.SLE_Model_Model.result import ResultPoint
from SLE_Model_Autolens.SLE_Model_Point.SLE_Model_Solver import PointSolver
from SLE_Model_Autolens import exc

try:
    import numba

    NumbaException = numba.errors.TypingError
except ModuleNotFoundError:
    NumbaException = ValueError


class AnalysisPoint(AgAnalysis, AnalysisLens):
    Result = ResultPoint

    def __init__(
        self,
        dataset,
        solver,
        fit_positions_cls=FitPositionsImagePairRepeat,
        image=None,
        cosmology=ag.cosmo.Planck15(),
        title_prefix=None,
    ):
        """
        The analysis performed for model-fitting a point-source dataset, for example fitting the point-sources of a
        multiply imaged lensed quasar or supernovae of many source galaxies of a galaxy cluster.

        The analysis brings together the data, model and non-linear search in the classes `log_likelihood_function`,
        which is called by every iteration of the non-linear search to compute a likelihood value which samples
        parameter space.

        Parameters
        ----------
        point_dict
            A dictionary containing the full point source dictionary that is used for model-fitting.
        solver
            The object which is used to determine the image-plane of source-plane positions of a model (via a `Tracer`).
        dataset
            The imaging of the point-source dataset, which is not used for model-fitting but can be used for
            visualization.
        cosmology
            The cosmology of the ray-tracing calculation.
        title_prefix
            A string that is added before the title of all figures output by visualization, for example to
            put the name of the dataset and galaxy in the title.
        """
        super().__init__(cosmology=cosmology)
        AnalysisLens.__init__(self=self, cosmology=cosmology)
        self.dataset = dataset
        self.solver = solver
        self.fit_positions_cls = fit_positions_cls
        self.title_prefix = title_prefix

    def log_likelihood_function(self, instance):
        """
        Determine the fit of the strong lens system of lens galaxies and source galaxies to the point source data.

        Parameters
        ----------
        instance
            A model instance with attributes

        Returns
        -------
        fit : Fit
            A fractional value indicating how well this model fit and the model masked_dataset itself
        """
        try:
            fit = self.fit_from(instance=instance)
            return fit.log_likelihood
        except (AttributeError, ValueError, TypeError, NumbaException) as e:
            raise exc.FitException from e

    def fit_from(self, instance, run_time_dict=None):
        tracer = self.tracer_via_instance_from(
            instance=instance, run_time_dict=run_time_dict
        )
        return FitPointDataset(
            dataset=self.dataset,
            tracer=tracer,
            solver=self.solver,
            fit_positions_cls=self.fit_positions_cls,
            run_time_dict=run_time_dict,
        )

    def visualize(self, paths, instance, during_analysis):
        tracer = self.tracer_via_instance_from(instance=instance)
        plotter_interface = PlotterInterface(image_path=paths.image_path)

    def save_attributes(self, paths):
        ag.output_to_json(
            obj=self.dataset, file_path=(paths._files_path / "dataset.json")
        )
