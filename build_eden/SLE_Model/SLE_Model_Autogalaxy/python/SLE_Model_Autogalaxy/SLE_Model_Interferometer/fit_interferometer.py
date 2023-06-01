import numpy as np
from typing import Dict, List, Optional
from SLE_Model_Autoconf import cached_property
import SLE_Model_Autoarray as aa
from SLE_Model_Autogalaxy.abstract_fit import AbstractFitInversion
from SLE_Model_Autogalaxy.SLE_Model_Analysis.preloads import Preloads
from SLE_Model_Autogalaxy.SLE_Model_Galaxy.galaxy import Galaxy
from SLE_Model_Autogalaxy.SLE_Model_Plane.plane import Plane
from SLE_Model_Autogalaxy.SLE_Model_Plane.to_inversion import PlaneToInversion


class FitInterferometer(aa.FitInterferometer, AbstractFitInversion):
    def __init__(
        self,
        dataset,
        plane,
        settings_pixelization=aa.SettingsPixelization(),
        settings_inversion=aa.SettingsInversion(),
        preloads=Preloads(),
        profiling_dict=None,
    ):
        """
        Fits an interferometer dataset using a `Plane` object.

        The fit performs the following steps:

        1) Compute the sum of all images of galaxy light profiles in the `Plane`.

        2) Fourier transform this image with the transformer object and `uv_wavelengths` to create
           the `profile_visibilities`.

        3) Subtract these visibilities from the `data` to create the `profile_subtracted_visibilities`.

        4) If the `Plane` has any linear algebra objects (e.g. linear light profiles, a pixelization / regulariation)
           fit the `profile_subtracted_visibilities` with these objects via an inversion.

        5) Compute the `model_data` as the sum of the `profile_visibilities` and `reconstructed_data` of the inversion
           (if an inversion is not performed the `model_data` is only the `profile_visibilities`.

        6) Subtract the `model_data` from the data and compute the residuals, chi-squared and likelihood via the
           noise-map (if an inversion is performed the `log_evidence`, including addition terms describing the linear
           algebra solution, is computed).

        When performing a model-fit` via ` AnalysisInterferometer` object the `figure_of_merit` of
        this `FitInterferometer` object is called and returned in the `log_likelihood_function`.

        Parameters
        ----------
        dataset
            The interfometer dataset which is fitted by the galaxies in the plane.
        plane
            The plane of galaxies whose light profile images are used to fit the interferometer data.
        settings_pixelization
            Settings controlling how a pixelization is fitted for example if a border is used when creating the
            pixelization.
        settings_inversion
            Settings controlling how an inversion is fitted for example which linear algebra formalism is used.
        preloads
            Contains preloaded calculations (e.g. linear algebra matrices) which can skip certain calculations in
            the fit.
        profiling_dict
            A dictionary which if passed to the fit records how long fucntion calls which have the `profile_func`
            decorator take to run.
        """
        try:
            from SLE_Model_Autoarray.SLE_Model_Inversion.SLE_Model_Inversion import (
                inversion_util_secret,
            )
        except ImportError:
            settings_inversion.use_w_tilde = False
        super().__init__(
            dataset=dataset, use_mask_in_fit=False, profiling_dict=profiling_dict
        )
        AbstractFitInversion.__init__(
            self=self, model_obj=plane, settings_inversion=settings_inversion
        )
        self.plane = plane
        self.settings_pixelization = settings_pixelization
        self.settings_inversion = settings_inversion
        self.preloads = preloads

    @property
    def profile_visibilities(self):
        """
        Returns the visibilities of every light profile of every galaxy in the plane, which are computed by performing
        a Fourier transform to the sum of light profile images.
        """
        return self.plane.visibilities_from(
            grid=self.dataset.grid, transformer=self.dataset.transformer
        )

    @property
    def profile_subtracted_visibilities(self):
        """
        Returns the interferometer dataset's visibilities with all transformed light profile images in the fit's
        plane subtracted.
        """
        return self.visibilities - self.profile_visibilities

    @property
    def plane_to_inversion(self):
        return PlaneToInversion(
            plane=self.plane,
            dataset=self.dataset,
            data=self.profile_subtracted_visibilities,
            noise_map=self.noise_map,
            w_tilde=self.w_tilde,
            settings_pixelization=self.settings_pixelization,
            settings_inversion=self.settings_inversion,
            preloads=self.preloads,
        )

    @cached_property
    def inversion(self):
        """
        If the plane has linear objects which are used to fit the data (e.g. a linear light profile / pixelization)
        this function returns a linear inversion, where the flux values of these objects (e.g. the `intensity`
        of linear light profiles) are computed via linear matrix algebra.

        The data passed to this function is the dataset's visibilities with all light profile visibilities of the
        plane subtracted.
        """
        if self.perform_inversion:
            return self.plane_to_inversion.inversion

    @property
    def model_data(self):
        """
        Returns the model data that is used to fit the data.

        If the plane does not have any linear objects and therefore omits an inversion, the model data is the
        sum of all light profile images Fourier transformed to visibilities.

        If a inversion is included it is the sum of these visibilities and the inversion's reconstructed visibilities.
        """
        if self.perform_inversion:
            return self.profile_visibilities + self.inversion.mapped_reconstructed_data
        return self.profile_visibilities

    @property
    def grid(self):
        return self.interferometer.grid

    @property
    def galaxies(self):
        return self.plane.galaxies

    @property
    def galaxy_model_image_dict(self):
        """
        A dictionary which associates every galaxy in the plane with its `image`.

        This image is the image of the sum of:

        - The images of all ordinary light profiles in that plane summed.
        - The images of all linear objects (e.g. linear light profiles / pixelizations), where the images are solved
          for first via the inversion.

        For modeling, this dictionary is used to set up the `adapt_images` that adapt certain pixelizations to the
        data being fitted.
        """
        galaxy_model_image_dict = self.plane.galaxy_image_2d_dict_from(grid=self.grid)
        galaxy_linear_obj_image_dict = self.galaxy_linear_obj_data_dict_from(
            use_image=True
        )
        return {**galaxy_model_image_dict, **galaxy_linear_obj_image_dict}

    @property
    def galaxy_model_visibilities_dict(self):
        """
        A dictionary which associates every galaxy in the plane with its model visibilities.

        These visibilities are the sum of:

        - The visibilities of all ordinary light profiles in that plane summed and Fourier transformed to visibilities
          space.
        - The visibilities of all linear objects (e.g. linear light profiles / pixelizations), where the visibilities
          are solved for first via the inversion.

        For modeling, this dictionary is used to set up the `adapt_visibilities` that adapt certain pixelizations to the
        data being fitted.
        """
        galaxy_model_visibilities_dict = self.plane.galaxy_visibilities_dict_from(
            grid=self.interferometer.grid, transformer=self.interferometer.transformer
        )
        galaxy_linear_obj_data_dict = self.galaxy_linear_obj_data_dict_from(
            use_image=False
        )
        return {**galaxy_model_visibilities_dict, **galaxy_linear_obj_data_dict}

    @property
    def model_visibilities_of_galaxies_list(self):
        """
        A list of the model visibilities of each galaxy in the plane.
        """
        return list(self.galaxy_model_visibilities_dict.values())

    @property
    def plane_linear_light_profiles_to_light_profiles(self):
        """
        The `Plane` where all linear light profiles have been converted to ordinary light profiles, where their
        `intensity` values are set to the values inferred by this fit.

        This is typically used for visualization, because linear light profiles cannot be used in `LightProfilePlotter`
        or `GalaxyPlotter` objects.
        """
        return self.model_obj_linear_light_profiles_to_light_profiles

    def refit_with_new_preloads(self, preloads, settings_inversion=None):
        """
        Returns a new fit which uses the dataset, plane and other objects of this fit, but uses a different set of
        preloads input into this function.

        This is used when setting up the preloads objects, to concisely test how using different preloads objects
        changes the attributes of the fit.

        Parameters
        ----------
        preloads
            The new preloads which are used to refit the data using the
        settings_inversion
            Settings controlling how an inversion is fitted for example which linear algebra formalism is used.

        Returns
        -------
        A new fit which has used new preloads input into this function but the same dataset, plane and other settings.
        """
        if self.profiling_dict is not None:
            profiling_dict = {}
        else:
            profiling_dict = None
        if settings_inversion is None:
            settings_inversion = self.settings_inversion
        return FitInterferometer(
            dataset=self.interferometer,
            plane=self.plane,
            settings_pixelization=self.settings_pixelization,
            settings_inversion=settings_inversion,
            preloads=preloads,
            profiling_dict=profiling_dict,
        )