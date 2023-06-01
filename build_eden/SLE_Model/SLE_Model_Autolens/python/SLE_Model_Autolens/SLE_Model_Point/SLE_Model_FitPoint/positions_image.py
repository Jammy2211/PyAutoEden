from functools import partial
from typing import Optional
import SLE_Model_Autoarray as aa
import SLE_Model_Autogalaxy as ag
from SLE_Model_Autolens.SLE_Model_Point.point_dataset import PointDict
from SLE_Model_Autolens.SLE_Model_Point.point_dataset import PointDataset
from SLE_Model_Autolens.SLE_Model_Point.point_solver import PointSolver
from SLE_Model_Autolens.SLE_Model_Lens.ray_tracing import Tracer
from SLE_Model_Autolens import exc


class FitPositionsImage(aa.FitDataset):
    def __init__(
        self, name, positions, noise_map, tracer, point_solver, point_profile=None
    ):
        """
        A lens position fitter, which takes a set of positions (e.g. from a plane in the tracer) and computes         their maximum separation, such that points which tracer closer to one another have a higher log_likelihood.

        Parameters
        ----------
        positions : Grid2DIrregular
            The (y,x) arc-second coordinates of positions which the maximum distance and log_likelihood is computed using.
        noise_value
            The noise-value assumed when computing the log likelihood.
        """
        super().__init__(dataset=positions)
        self.name = name
        self._noise_map = noise_map
        self.tracer = tracer
        self.point_profile = (
            tracer.extract_profile(profile_name=name)
            if (point_profile is None)
            else point_profile
        )
        self.point_solver = point_solver
        if self.point_profile is None:
            raise exc.PointExtractionException(
                f"For the point-source named {name} there was no matching point source profile in the tracer (make sure your tracer's point source name is the same the dataset name."
            )
        self.source_plane_coordinate = self.point_profile.centre

    @property
    def mask(self):
        return None

    @property
    def noise_map(self):
        return self._noise_map

    @property
    def positions(self):
        return self.dataset

    @property
    def model_data(self):
        """
        Returns the model positions, which are computed via the point solver.

        It if common for many more image-plane positions to be computed than actual positions in the dataset. In this
        case, each data point is paired with its closest model position.
        """
        if len(self.tracer.planes) > 2:
            upper_plane_index = self.tracer.extract_plane_index_of_profile(
                profile_name=self.name
            )
        else:
            upper_plane_index = None
        model_positions = self.point_solver.solve(
            lensing_obj=self.tracer,
            source_plane_coordinate=self.source_plane_coordinate,
            upper_plane_index=upper_plane_index,
        )
        return model_positions.grid_of_closest_from(grid_pair=self.positions)

    @property
    def model_positions(self):
        return self.model_data

    @property
    def residual_map(self):
        residual_positions = self.positions - self.model_positions
        return residual_positions.distances_to_coordinate_from(coordinate=(0.0, 0.0))

    @property
    def chi_squared(self):
        """
        Returns the chi-squared terms of the model data's fit to an dataset, by summing the chi-squared-map.
        """
        return ag.util.fit.chi_squared_from(chi_squared_map=self.chi_squared_map)