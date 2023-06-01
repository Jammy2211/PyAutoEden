import logging
import numpy as np
import os
from typing import Optional, Union
import SLE_Model_Autofit as af
import SLE_Model_Autoarray as aa
import SLE_Model_Autogalaxy as ag
from SLE_Model_Autoarray.exc import PixelizationException
from SLE_Model_Autolens.SLE_Model_Analysis.analysis import AnalysisDataset
from SLE_Model_Autolens.SLE_Model_Analysis.preloads import Preloads
from SLE_Model_Autolens.SLE_Model_Analysis.positions import PositionsLHResample
from SLE_Model_Autolens.SLE_Model_Analysis.positions import PositionsLHPenalty
from SLE_Model_Autolens.SLE_Model_Lens.ray_tracing import Tracer
from SLE_Model_Autolens.SLE_Model_Interferometer.SLE_Model_Model.result import (
    ResultInterferometer,
)
from SLE_Model_Autolens.SLE_Model_Interferometer.SLE_Model_Model.visualizer import (
    VisualizerInterferometer,
)
from SLE_Model_Autolens.SLE_Model_Interferometer.fit_interferometer import (
    FitInterferometer,
)
from SLE_Model_Autolens.SLE_Model_Analysis.settings import SettingsLens
from SLE_Model_Autolens import exc

logger = logging.getLogger(__name__)
logger.setLevel(level="INFO")


class AnalysisInterferometer(AnalysisDataset):
    def __init__(
        self,
        dataset,
        positions_likelihood=None,
        adapt_result=None,
        cosmology=ag.cosmo.Planck15(),
        settings_pixelization=None,
        settings_inversion=None,
        settings_lens=None,
        raise_inversion_positions_likelihood_exception=True,
    ):
        """
        Analysis classes are used by PyAutoFit to fit a model to a dataset via a non-linear search.

        An Analysis class defines the `log_likelihood_function` which fits the model to the dataset and returns the
        log likelihood value defining how well the model fitted the data. The Analysis class handles many other tasks,
        such as visualization, outputting results to hard-disk and storing results in a format that can be loaded after
        the model-fit is complete using PyAutoFit's database tools.

        This Analysis class is used for all model-fits which fit galaxies (or objects containing galaxies like a
        `Tracer`) to an interferometer dataset.

        This class stores the settings used to perform the model-fit for certain components of the model (e.g. a
        pixelization or inversion), the Cosmology used for the analysis and hyper datasets used for certain model
        classes.

        Parameters
        ----------
        dataset
            The interferometer dataset that the model is fitted too.
        positions_likelihood
            An object which alters the likelihood function to include a term which accounts for whether
            image-pixel coordinates in arc-seconds corresponding to the multiple images of the lensed source galaxy
            trace close to one another in the source-plane.
        adapt_result
            The hyper-model image and galaxies images of a previous result in a model-fitting pipeline, which are
            used by certain classes for adapting the analysis to the properties of the dataset.
        cosmology
            The Cosmology assumed for this analysis.
        settings_pixelization
            settings controlling how a pixelization is fitted for example if a border is used when creating the
            pixelization.
        settings_inversion
            Settings controlling how an inversion is fitted, for example which linear algebra formalism is used.
        settings_lens
            Settings controlling the lens calculation, for example how close the lensed source's multiple images have
            to trace within one another in the source plane for the model to not be discarded.
        raise_inversion_positions_likelihood_exception
            If an inversion is used without the `positions_likelihood` it is likely a systematic solution will
            be inferred, in which case an Exception is raised before the model-fit begins to inform the user
            of this. This exception is not raised if this input is False, allowing the user to perform the model-fit
            anyway.
        """
        super().__init__(
            dataset=dataset,
            positions_likelihood=positions_likelihood,
            adapt_result=adapt_result,
            cosmology=cosmology,
            settings_pixelization=settings_pixelization,
            settings_inversion=settings_inversion,
            settings_lens=settings_lens,
            raise_inversion_positions_likelihood_exception=raise_inversion_positions_likelihood_exception,
        )
        if self.adapt_result is not None:
            self.set_adapt_dataset(result=self.adapt_result)
        else:
            self.adapt_galaxy_visibilities_path_dict = None
            self.adapt_model_visibilities = None

    @property
    def interferometer(self):
        return self.dataset

    def modify_before_fit(self, paths, model):
        """
        PyAutoFit calls this function immediately before the non-linear search begins, therefore it can be used to
        perform tasks using the final model parameterization.

        This function checks that the adapt-dataset is consistent with previous adapt-datasets if the model-fit is
        being resumed from a previous run, and it visualizes objects which do not change throughout the model fit
        like the dataset.

        Parameters
        ----------
        paths
            The PyAutoFit paths object which manages all paths, e.g. where the non-linear search outputs are stored,
            visualization and the pickled objects used by the aggregator output by this function.
        model
            The PyAutoFit model object, which includes model components representing the galaxies that are fitted to
            the imaging data.
        """
        super().modify_before_fit(paths=paths, model=model)
        if not paths.is_complete:
            logger.info(
                "PRELOADS - Setting up preloads, may take a few minutes for fits using an inversion."
            )
            self.set_preloads(paths=paths, model=model)
        return self

    def set_adapt_dataset(self, result):
        """
        Using a the result of a previous model-fit, set the adapt-dataset for this analysis. This is used to adapt
        aspects of the model (e.g. the pixelization, regularization scheme) to the properties of the dataset being
        fitted.

        This passes the adapt image and galaxy images of the previous fit. These represent where different
        galaxies in the dataset are located and thus allows the fit to adapt different aspects of the model to
        different galaxies in the data.

        It also passes hyper visibilities, which are used to scale the noise of a visibility dataset.

        Parameters
        ----------
        result
            The result of a previous model-fit which contains the model image and model galaxy images of a fit to
            the dataset, which set up the hyper dataset. These are used by certain classes for adapting the analysis
            to the properties of the dataset.
        """
        super().set_adapt_dataset(result=result)
        self.adapt_model_visibilities = result.adapt_model_visibilities
        self.adapt_galaxy_visibilities_path_dict = (
            result.adapt_galaxy_visibilities_path_dict
        )

    def instance_with_associated_hyper_visibilities_from(self, instance):
        """
        Using the model visibilities that were set up as the hyper dataset, associate the galaxy images of that result
        with the galaxies in this model fit.

        Association is performed based on galaxy names, whereby if the name of a galaxy in this search matches the
        full-path name of galaxies in the hyper dataset the galaxy image is passed.

        If the galaxy collection has a different name then an association is not made.

        For example, `galaxies.lens` will match with:
            `galaxies.lens`
        but not with:
            `galaxies.source`

        Parameters
        ----------
        instance
            An instance of the model that is being fitted to the data by this analysis (whose parameters have been set
            via a non-linear search), which has 0 or more galaxies in its tree.

        Returns
        -------
        instance
           The input instance with visibilities associated with galaxies where possible.
        """
        if self.adapt_galaxy_visibilities_path_dict is not None:
            for (galaxy_path, galaxy) in instance.path_instance_tuples_for_class(
                ag.Galaxy
            ):
                if galaxy_path in self.adapt_galaxy_visibilities_path_dict:
                    galaxy.adapt_model_visibilities = self.adapt_model_visibilities
                    galaxy.adapt_galaxy_visibilities = (
                        self.adapt_galaxy_visibilities_path_dict[galaxy_path]
                    )
        return instance

    def log_likelihood_function(self, instance):
        """
        Given an instance of the model, where the model parameters are set via a non-linear search, fit the model
        instance to the interferometer dataset.

        This function returns a log likelihood which is used by the non-linear search to guide the model-fit.

        For this analysis class, this function performs the following steps:

        1) If the analysis has a hyper dataset, associated the model galaxy images of this dataset to the galaxies in
           the model instance.

        2) Extract attributes which model aspects of the data reductions, like the scaling the background sky
           and background noise.

        3) Extracts all galaxies from the model instance and set up a `Tracer`, which includes ordering the galaxies
           by redshift to set up each `Plane`.

        4) Use the `Tracer` and other attributes to create a `FitInterferometer` object, which performs steps such as
           creating model images of every galaxy in the plane, transforming them to the uv-plane via a Fourier transform
           and computing residuals, a chi-squared statistic and the log likelihood.

        Certain models will fail to fit the dataset and raise an exception. For example if an `Inversion` is used, the
        linear algebra calculation may be invalid and raise an Exception. In such circumstances the model is discarded
        and its likelihood value is passed to the non-linear search in a way that it ignores it (for example, using a
        value of -1.0e99).

        Parameters
        ----------
        instance
            An instance of the model that is being fitted to the data by this analysis (whose parameters have been set
            via a non-linear search).

        Returns
        -------
        float
            The log likelihood indicating how well this model instance fitted the interferometer data.
        """
        try:
            log_likelihood_positions_overwrite = (
                self.log_likelihood_positions_overwrite_from(instance=instance)
            )
            if log_likelihood_positions_overwrite is not None:
                return log_likelihood_positions_overwrite
        except Exception as e:
            raise e
        try:
            return self.fit_interferometer_via_instance_from(
                instance=instance
            ).figure_of_merit
        except (
            PixelizationException,
            exc.PixelizationException,
            exc.InversionException,
            exc.GridException,
            ValueError,
            TypeError,
            np.linalg.LinAlgError,
            OverflowError,
        ) as e:
            raise exc.FitException from e

    def fit_interferometer_via_instance_from(self, instance, preload_overwrite=None):
        """
        Given a model instance create a `FitInterferometer` object.

        This function is used in the `log_likelihood_function` to fit the model to the interferometer data and compute
        the log likelihood.

        Parameters
        ----------
        instance
            An instance of the model that is being fitted to the data by this analysis (whose parameters have been set
            via a non-linear search).
        preload_overwrite
            If a `Preload` object is input this is used instead of the preloads stored as an attribute in the analysis.
        check_positions
            Whether the multiple image positions of the lensed source should be checked, i.e. whether they trace
            within the position threshold of one another in the source plane.
        profiling_dict
            A dictionary which times functions called to fit the model to data, for profiling.

        Returns
        -------
        FitInterferometer
            The fit of the plane to the interferometer dataset, which includes the log likelihood.
        """
        self.instance_with_associated_adapt_images_from(instance=instance)
        tracer = self.tracer_via_instance_from(instance=instance)
        return self.fit_interferometer_via_tracer_from(tracer=tracer)

    def fit_interferometer_via_tracer_from(self, tracer, preload_overwrite=None):
        """
        Given a `Tracer`, which the analysis constructs from a model instance, create a `FitInterferometer` object.

        This function is used in the `log_likelihood_function` to fit the model to the imaging data and compute the
        log likelihood.

        Parameters
        ----------
        tracer
            The tracer of galaxies whose ray-traced model images are used to fit the imaging data.
        preload_overwrite
            If a `Preload` object is input this is used instead of the preloads stored as an attribute in the analysis.
        profiling_dict
            A dictionary which times functions called to fit the model to data, for profiling.

        Returns
        -------
        FitImaging
            The fit of the plane to the imaging dataset, which includes the log likelihood.
        """
        preloads = self.preloads if (preload_overwrite is None) else preload_overwrite
        return FitInterferometer(
            dataset=self.dataset,
            tracer=tracer,
            settings_pixelization=self.settings_pixelization,
            settings_inversion=self.settings_inversion,
            preloads=preloads,
        )

    @property
    def fit_func(self):
        return self.fit_interferometer_via_instance_from

    def stochastic_log_likelihoods_via_instance_from(self, instance):
        """
         Certain `Inversion`'s have stochasticity in their log likelihood estimate.

         For example, the `VoronoiBrightnessImage` pixelization, which changes the likelihood depending on how different
         KMeans seeds change the pixel-grid.

         A log likelihood cap can be applied to model-fits performed using these `Inversion`'s to improve error and
         posterior estimates. This log likelihood cap is estimated from a list of stochastic log likelihoods, where
         these log likelihoods are computed using the same model but with different KMeans seeds.

         This function computes these stochastic log likelihoods by iterating over many model-fits using different
         KMeans seeds.

         Parameters
         ----------
        instance
             The maximum log likelihood instance of a model that is has finished being fitted to the dataset.

         Returns
         -------
         float
             A log likelihood cap which is applied in a stochastic model-fit to give improved error and posterior
             estimates.
        """
        instance = self.instance_with_associated_adapt_images_from(instance=instance)
        tracer = self.tracer_via_instance_from(instance=instance)
        if not tracer.has(cls=aa.Pixelization):
            return None
        if not any(
            [
                pix.mesh.is_stochastic
                for pix in tracer.cls_list_from(cls=ag.Pixelization)
            ]
        ):
            return
        settings_pixelization = (
            self.settings_pixelization.settings_with_is_stochastic_true()
        )
        log_evidences = []
        for i in range(self.settings_lens.stochastic_samples):
            try:
                log_evidence = FitInterferometer(
                    dataset=self.dataset,
                    tracer=tracer,
                    settings_pixelization=settings_pixelization,
                    settings_inversion=self.settings_inversion,
                    preloads=self.preloads,
                ).log_evidence
            except (
                PixelizationException,
                exc.PixelizationException,
                exc.InversionException,
                exc.GridException,
                OverflowError,
            ) as e:
                log_evidence = None
            if log_evidence is not None:
                log_evidences.append(log_evidence)
        return log_evidences

    def visualize_before_fit(self, paths, model):
        """
        PyAutoFit calls this function immediately before the non-linear search begins.

        It visualizes objects which do not change throughout the model fit like the dataset.

        Parameters
        ----------
        paths
            The PyAutoFit paths object which manages all paths, e.g. where the non-linear search outputs are stored,
            visualization and the pickled objects used by the aggregator output by this function.
        model
            The PyAutoFit model object, which includes model components representing the galaxies that are fitted to
            the imaging data.
        """
        if not self.should_visualize(paths=paths):
            return
        visualizer = VisualizerInterferometer(visualize_path=paths.image_path)
        visualizer.visualize_interferometer(interferometer=self.interferometer)
        if self.positions_likelihood is not None:
            visualizer.visualize_image_with_positions(
                image=self.interferometer.dirty_image,
                positions=self.positions_likelihood.positions,
            )
        visualizer.visualize_adapt_images(
            adapt_galaxy_image_path_dict=self.adapt_galaxy_image_path_dict,
            adapt_model_image=self.adapt_model_image,
        )

    def visualize(self, paths, instance, during_analysis):
        """
        Outputs images of the maximum log likelihood model inferred by the model-fit. This function is called
        throughout the non-linear search at input intervals, and therefore provides on-the-fly visualization of how
        well the model-fit is going.

        The visualization performed by this function includes:

        - Images of the best-fit `Tracer`, including the images of each of its galaxies.

        - Images of the best-fit `FitInterferometer`, including the model-image, residuals and chi-squared of its fit
          to the imaging data.

        - The hyper-images of the model-fit showing how the galaxies are used to represent different galaxies in
          the dataset.

        - If hyper features are used to scale the noise, a `FitInterferometer` with these features turned off may be
          output, to indicate how much these features are altering the dataset.

        The images output by this function are customized using the file `config/visualize/plots.ini`.

        Parameters
        ----------
        paths
            The PyAutoFit paths object which manages all paths, e.g. where the non-linear search outputs are stored,
            visualization, and the pickled objects used by the aggregator output by this function.
        instance
            An instance of the model that is being fitted to the data by this analysis (whose parameters have been set
            via a non-linear search).
        during_analysis
            If True the visualization is being performed midway through the non-linear search before it is finished,
            which may change which images are output.
        """
        if not self.should_visualize(paths=paths):
            return
        instance = self.instance_with_associated_adapt_images_from(instance=instance)
        fit = self.fit_interferometer_via_instance_from(instance=instance)
        if self.positions_likelihood is not None:
            self.positions_likelihood.output_positions_info(
                output_path=paths.output_path, tracer=fit.tracer
            )
        if fit.inversion is not None:
            try:
                fit.inversion.reconstruction
            except exc.InversionException:
                return
        visualizer = VisualizerInterferometer(visualize_path=paths.image_path)
        try:
            visualizer.visualize_fit_interferometer(
                fit=fit, during_analysis=during_analysis
            )
        except exc.InversionException:
            pass
        tracer = fit.tracer_linear_light_profiles_to_light_profiles
        visualizer.visualize_tracer(
            tracer=tracer, grid=fit.grid, during_analysis=during_analysis
        )
        visualizer.visualize_galaxies(
            galaxies=tracer.galaxies, grid=fit.grid, during_analysis=during_analysis
        )
        if fit.inversion is not None:
            try:
                visualizer.visualize_inversion(
                    inversion=fit.inversion, during_analysis=during_analysis
                )
            except IndexError:
                pass
        visualizer.visualize_contribution_maps(tracer=fit.tracer)

    def make_result(self, samples, model, sigma=1.0, use_errors=True, use_widths=False):
        """
        After the non-linear search is complete create its `Result`, which includes:

        - The samples of the non-linear search (E.g. MCMC chains, nested sampling samples) which are used to compute
          the maximum likelihood model, posteriors and other properties.

        - The model used to fit the data, which uses the samples to create specific instances of the model (e.g.
          an instance of the maximum log likelihood model).

        - The non-linear search used to perform the model fit.

        The `ResultInterferometer` object contains a number of methods which use the above objects to create the max
        log likelihood `Plane`, `FitInterferometer`, adapt-galaxy images,etc.

        Parameters
        ----------
        samples
            A PyAutoFit object which contains the samples of the non-linear search, for example the chains of an MCMC
            run of samples of the nested sampler.
        model
            The PyAutoFit model object, which includes model components representing the galaxies that are fitted to
            the imaging data.

        Returns
        -------
        ResultImaging
            The result of fitting the model to the imaging dataset, via a non-linear search.
        """
        return ResultInterferometer(samples=samples, model=model, analysis=self)

    def save_attributes_for_aggregator(self, paths):
        """
         Before the non-linear search begins, this routine saves attributes of the `Analysis` object to the `pickles`
         folder such that they can be loaded after the analysis using PyAutoFit's database and aggregator tools.

         For this analysis, it uses the `AnalysisDataset` object's method to output the following:

         - The dataset's data.
         - The dataset's noise-map.
         - The settings associated with the dataset.
         - The settings associated with the inversion.
         - The settings associated with the pixelization.
         - The Cosmology.
         - The hyper dataset's model image and galaxy images, if used.

         This function also outputs attributes specific to an imaging dataset:

        - Its uv-wavelengths
        - Its real space mask.
        - The positions of the brightest pixels in the lensed source which are used to discard mass models.
        - The preloaded image-plane source plane pixelization if used by the analysis. This ensures that differences in
        the scikit-learn library do not lead to different pixelizations being computed if results are transferred from
        a HPC to laptop.

         It is common for these attributes to be loaded by many of the template aggregator functions given in the
         `aggregator` modules. For example, when using the database tools to perform a fit, the default behaviour is for
         the dataset, settings and other attributes necessary to perform the fit to be loaded via the pickle files
         output by this function.

         Parameters
         ----------
         paths
             The PyAutoFit paths object which manages all paths, e.g. where the non-linear search outputs are stored,
             visualization, and the pickled objects used by the aggregator output by this function.
        """
        super().save_attributes_for_aggregator(paths=paths)
        paths.save_object("uv_wavelengths", self.dataset.uv_wavelengths)
        paths.save_object("real_space_mask", self.dataset.real_space_mask)
        paths.save_object("positions_likelihood", self.positions_likelihood)
        if self.preloads.sparse_image_plane_grid_pg_list is not None:
            paths.save_object(
                "preload_sparse_grids_of_planes",
                self.preloads.sparse_image_plane_grid_pg_list,
            )