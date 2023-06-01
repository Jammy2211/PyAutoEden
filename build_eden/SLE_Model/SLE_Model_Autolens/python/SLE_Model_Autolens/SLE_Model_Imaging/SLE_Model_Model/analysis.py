import json
import logging
import numpy as np
import os
import time
from typing import Dict, Optional
from os import path
from SLE_Model_Autoconf import conf
import SLE_Model_Autofit as af
import SLE_Model_Autogalaxy as ag
from SLE_Model_Autoarray.exc import PixelizationException
from SLE_Model_Autolens.SLE_Model_Analysis.analysis import AnalysisDataset
from SLE_Model_Autolens.SLE_Model_Analysis.preloads import Preloads
from SLE_Model_Autolens.SLE_Model_Lens.ray_tracing import Tracer
from SLE_Model_Autolens.SLE_Model_Imaging.SLE_Model_Model.result import ResultImaging
from SLE_Model_Autolens.SLE_Model_Imaging.SLE_Model_Model.visualizer import (
    VisualizerImaging,
)
from SLE_Model_Autolens.SLE_Model_Imaging.fit_imaging import FitImaging
from SLE_Model_Autolens import exc

logger = logging.getLogger(__name__)
logger.setLevel(level="INFO")


class AnalysisImaging(AnalysisDataset):
    @property
    def imaging(self):
        return self.dataset

    def modify_before_fit(self, paths, model):
        """
        PyAutoFit calls this function immediately before the non-linear search begins, therefore it can be used to
        perform tasks using the final model parameterization.

        This function:

        - Checks that the adapt-dataset is consistent with previous adapt-datasets if the model-fit is being
          resumed from a previous run.

        - Checks the model and raises exceptions if certain critieria are not met.

        Once inherited from it also visualizes objects which do not change throughout the model fit like the dataset.

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
            self.set_preloads(paths=paths, model=model)
        return self

    def log_likelihood_function(self, instance):
        """
        Given an instance of the model, where the model parameters are set via a non-linear search, fit the model
        instance to the imaging dataset.

        This function returns a log likelihood which is used by the non-linear search to guide the model-fit.

        For this analysis class, this function performs the following steps:

        1) If the analysis has a hyper dataset, associated the model galaxy images of this dataset to the galaxies in
           the model instance.

        2) Extract attributes which model aspects of the data reductions, like the scaling the background sky
           and background noise.

        3) Extracts all galaxies from the model instance and set up a `Tracer`, which includes ordering the galaxies
           by redshift to set up each `Plane`.

        4) Use the `Tracer` and other attributes to create a `FitImaging` object, which performs steps such as creating
           model images of every galaxy in the tracer, blurring them with the imaging dataset's PSF and computing
           residuals, a chi-squared statistic and the log likelihood.

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
            The log likelihood indicating how well this model instance fitted the imaging data.
        """
        try:
            log_likelihood_positions_overwrite = (
                self.log_likelihood_positions_overwrite_from(instance=instance)
            )
            if log_likelihood_positions_overwrite is not None:
                return log_likelihood_positions_overwrite
        except Exception as e:
            raise e
        if log_likelihood_positions_overwrite is not None:
            return log_likelihood_positions_overwrite
        try:
            return self.fit_imaging_via_instance_from(instance=instance).figure_of_merit
        except (
            PixelizationException,
            exc.PixelizationException,
            exc.InversionException,
            exc.GridException,
            exc.MeshException,
            ValueError,
            TypeError,
            np.linalg.LinAlgError,
            OverflowError,
        ) as e:
            raise exc.FitException from e

    def fit_imaging_via_instance_from(
        self, instance, preload_overwrite=None, profiling_dict=None
    ):
        """
        Given a model instance create a `FitImaging` object.

        This function is used in the `log_likelihood_function` to fit the model to the imaging data and compute the
        log likelihood.

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
        FitImaging
            The fit of the plane to the imaging dataset, which includes the log likelihood.
        """
        self.instance_with_associated_adapt_images_from(instance=instance)
        tracer = self.tracer_via_instance_from(
            instance=instance, profiling_dict=profiling_dict
        )
        return self.fit_imaging_via_tracer_from(
            tracer=tracer,
            preload_overwrite=preload_overwrite,
            profiling_dict=profiling_dict,
        )

    def fit_imaging_via_tracer_from(
        self, tracer, preload_overwrite=None, profiling_dict=None
    ):
        """
        Given a `Tracer`, which the analysis constructs from a model instance, create a `FitImaging` object.

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
        preloads = preload_overwrite or self.preloads
        return FitImaging(
            dataset=self.dataset,
            tracer=tracer,
            settings_pixelization=self.settings_pixelization,
            settings_inversion=self.settings_inversion,
            preloads=preloads,
            profiling_dict=profiling_dict,
        )

    @property
    def fit_func(self):
        return self.fit_imaging_via_instance_from

    def profile_log_likelihood_function(self, instance, paths=None):
        """
        This function is optionally called throughout a model-fit to profile the log likelihood function.

        All function calls inside the `log_likelihood_function` that are decorated with the `profile_func` are timed
        with their times stored in a dictionary called the `profiling_dict`.

        An `info_dict` is also created which stores information no aspects of the model and dataset that dictate
        run times, so the profiled times can be interpreted with this context.

        The results of this profiling are then output to hard-disk in the `preloads` folder of the model-fit results,
        which they can be inspected to ensure run-times are as expected.

        Parameters
        ----------
        instance
            An instance of the model that is being fitted to the data by this analysis (whose parameters have been set
            via a non-linear search).
        paths
            The PyAutoFit paths object which manages all paths, e.g. where the non-linear search outputs are stored,
            visualization and the pickled objects used by the aggregator output by this function.
        """
        profiling_dict = {}
        info_dict = {}
        repeats = conf.instance["general"]["profiling"]["repeats"]
        info_dict["repeats"] = repeats
        start = time.time()
        for i in range(repeats):
            try:
                fit = self.fit_imaging_via_instance_from(instance=instance)
                fit.figure_of_merit
            except Exception:
                logger.info(
                    "Profiling failed. Returning without outputting information."
                )
                return
        fit_time = (time.time() - start) / repeats
        info_dict["fit_time"] = fit_time
        fit = self.fit_imaging_via_instance_from(
            instance=instance, profiling_dict=profiling_dict
        )
        fit.figure_of_merit
        info_dict["image_pixels"] = self.imaging.grid.sub_shape_slim
        info_dict["sub_size_light_profiles"] = self.imaging.grid.sub_size
        info_dict["sub_size_pixelization"] = self.imaging.grid_pixelization.sub_size
        info_dict["psf_shape_2d"] = self.imaging.psf.shape_native
        if fit.inversion is not None:
            info_dict["source_pixels"] = len(fit.inversion.reconstruction)
        if hasattr(fit.inversion, "w_tilde"):
            info_dict[
                "w_tilde_curvature_preload_size"
            ] = fit.inversion.w_tilde.curvature_preload.shape[0]
        if paths is not None:
            try:
                os.makedirs(paths.profile_path)
            except FileExistsError:
                pass
            with open(path.join(paths.profile_path, "profiling_dict.json"), "w+") as f:
                json.dump(fit.profiling_dict, f, indent=4)
            with open(path.join(paths.profile_path, "info_dict.json"), "w+") as f:
                json.dump(info_dict, f, indent=4)
        return profiling_dict

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
        if not tracer.has(cls=ag.Pixelization):
            return
        if not any(
            (
                pix.mesh.is_stochastic
                for pix in tracer.cls_list_from(cls=ag.Pixelization)
            )
        ):
            return
        settings_pixelization = (
            self.settings_pixelization.settings_with_is_stochastic_true()
        )
        log_evidences = []
        for i in range(self.settings_lens.stochastic_samples):
            try:
                log_evidence = FitImaging(
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
        visualizer = VisualizerImaging(visualize_path=paths.image_path)
        visualizer.visualize_imaging(imaging=self.imaging)
        if self.positions_likelihood is not None:
            visualizer.visualize_image_with_positions(
                image=self.imaging.image, positions=self.positions_likelihood.positions
            )
        visualizer.visualize_adapt_images(
            adapt_galaxy_image_path_dict=self.adapt_galaxy_image_path_dict,
            adapt_model_image=self.adapt_model_image,
        )

    def visualize(self, paths, instance, during_analysis):
        """
        Output images of the maximum log likelihood model inferred by the model-fit. This function is called throughout
        the non-linear search at regular intervals, and therefore provides on-the-fly visualization of how well the
        model-fit is going.

        The visualization performed by this function includes:

        - Images of the best-fit `Tracer`, including the images of each of its galaxies.

        - Images of the best-fit `FitImaging`, including the model-image, residuals and chi-squared of its fit to
          the imaging data.

        - The hyper-images of the model-fit showing how the galaxies are used to represent different galaxies in
          the dataset.

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
        fit = self.fit_imaging_via_instance_from(instance=instance)
        if self.positions_likelihood is not None:
            self.positions_likelihood.output_positions_info(
                output_path=paths.output_path, tracer=fit.tracer
            )
        if fit.inversion is not None:
            try:
                fit.inversion.reconstruction
            except exc.InversionException:
                return
        visualizer = VisualizerImaging(visualize_path=paths.image_path)
        try:
            visualizer.visualize_fit_imaging(fit=fit, during_analysis=during_analysis)
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
            if fit.inversion.has(cls=ag.AbstractMapper):
                visualizer.visualize_inversion(
                    inversion=fit.inversion, during_analysis=during_analysis
                )
        visualizer.visualize_contribution_maps(tracer=fit.tracer)

    def make_result(self, samples, model, sigma=1.0, use_errors=True, use_widths=False):
        """
        After the non-linear search is complete create its `Result`, which includes:

        - The samples of the non-linear search (E.g. MCMC chains, nested sampling samples) which are used to compute
          the maximum likelihood model, posteriors and other properties.

        - The model used to fit the data, which uses the samples to create specific instances of the model (e.g.
          an instance of the maximum log likelihood model).

        - The non-linear search used to perform the model fit.

        The `ResultImaging` object contains a number of methods which use the above objects to create the max
        log likelihood `Tracer`, `FitImaging`, adapt-galaxy images,etc.

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
        return ResultImaging(samples=samples, model=model, analysis=self)

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

        - Its PSF.
        - Its mask.
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
        paths.save_object("psf", self.dataset.psf)
        paths.save_object("mask", self.dataset.mask)
        paths.save_object("positions_likelihood", self.positions_likelihood)