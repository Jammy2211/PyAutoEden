from __future__ import annotations
from typing import TYPE_CHECKING, Optional, List

if TYPE_CHECKING:
    from SLE_Model_Autogalaxy.SLE_Model_Galaxy.galaxy import Galaxy
    from SLE_Model_Autogalaxy.SLE_Model_Imaging.fit_imaging import FitImaging
import SLE_Model_Autofit as af
import SLE_Model_Autoarray as aa
from SLE_Model_Autogalaxy.SLE_Model_Aggregator.abstract import AbstractAgg
from SLE_Model_Autogalaxy.SLE_Model_Aggregator.imaging import _imaging_from
from SLE_Model_Autogalaxy.SLE_Model_Analysis.preloads import Preloads
from SLE_Model_Autogalaxy.SLE_Model_Aggregator.plane import _plane_from


def _fit_imaging_from(
    fit,
    galaxies,
    settings_imaging=None,
    settings_pixelization=None,
    settings_inversion=None,
    use_preloaded_grid=True,
):
    """
    Returns a `FitImaging` object from a PyAutoFit database `Fit` object and an instance of galaxies from a non-linear
    search model-fit.

    This function adds the `adapt_model_image` and `adapt_galaxy_image_path_dict` to the galaxies before performing the
    fit, if they were used.

    Parameters
    ----------
    fit
        A PyAutoFit database Fit object containing the generators of the results of model-fits.
    galaxies
        A list of galaxies corresponding to a sample of a non-linear search and model-fit.

    Returns
    -------
    FitImaging
        The fit to the imaging dataset computed via an instance of galaxies.
    """
    from SLE_Model_Autogalaxy.SLE_Model_Imaging.fit_imaging import FitImaging

    imaging = _imaging_from(fit=fit, settings_imaging=settings_imaging)
    plane = _plane_from(fit=fit, galaxies=galaxies)
    settings_pixelization = settings_pixelization or fit.value(
        name="settings_pixelization"
    )
    settings_inversion = settings_inversion or fit.value(name="settings_inversion")
    preloads = Preloads(use_w_tilde=False)
    if use_preloaded_grid:
        sparse_grids_of_planes = fit.value(name="preload_sparse_grids_of_planes")
        if sparse_grids_of_planes is not None:
            preloads = Preloads(
                sparse_image_plane_grid_pg_list=sparse_grids_of_planes,
                use_w_tilde=False,
            )
            if len(preloads.sparse_image_plane_grid_pg_list) == 2:
                if type(preloads.sparse_image_plane_grid_pg_list[1]) != list:
                    preloads.sparse_image_plane_grid_pg_list[1] = [
                        preloads.sparse_image_plane_grid_pg_list[1]
                    ]
    return FitImaging(
        dataset=imaging,
        plane=plane,
        settings_pixelization=settings_pixelization,
        settings_inversion=settings_inversion,
        preloads=preloads,
    )


class FitImagingAgg(AbstractAgg):
    def __init__(
        self,
        aggregator,
        settings_imaging=None,
        settings_pixelization=None,
        settings_inversion=None,
        use_preloaded_grid=True,
    ):
        """
        Wraps a PyAutoFit aggregator in order to create generators of fits to imaging data, corresponding to the
        results of a non-linear search model-fit.
        """
        super().__init__(aggregator=aggregator)
        self.settings_imaging = settings_imaging
        self.settings_pixelization = settings_pixelization
        self.settings_inversion = settings_inversion
        self.use_preloaded_grid = use_preloaded_grid

    def object_via_gen_from(self, fit, galaxies):
        """
        Creates a `FitImaging` object from a `ModelInstance` that contains the galaxies of a sample from a non-linear
        search.

        Parameters
        ----------
        fit
            A PyAutoFit database Fit object containing the generators of the results of model-fits.
        galaxies
            A list of galaxies corresponding to a sample of a non-linear search and model-fit.

        Returns
        -------
        FitImaging
            A fit to imaging data whose galaxies are a sample of a PyAutoFit non-linear search.
        """
        return _fit_imaging_from(
            fit=fit,
            galaxies=galaxies,
            settings_imaging=self.settings_imaging,
            settings_pixelization=self.settings_pixelization,
            settings_inversion=self.settings_inversion,
            use_preloaded_grid=self.use_preloaded_grid,
        )
