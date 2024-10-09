from typing import Optional
import SLE_Model_Autofit as af
import SLE_Model_Autogalaxy as ag


class SetupAdapt(ag.SetupAdapt):
    def __init__(
        self, search_pix_cls=None, search_pix_dict=None, mesh_pixels_fixed=None
    ):
        """
        The adapt setup of a pipeline, which controls how adaptive-features in PyAutoLens template pipelines run,
        for example controlling whether galaxies are used to scale the noise and the non-linear searches used
        in these searchs.

        Users can write their own pipelines which do not use or require the *SetupAdapt* class.

        Parameters
        ----------
        search_pix_cls
            The non-linear search used by every adapt model-fit search.
        search_pix_dict
            The dictionary of search options for the adapt model-fit searches.
        """
        super().__init__(
            search_pix_cls=search_pix_cls,
            search_pix_dict=search_pix_dict,
            mesh_pixels_fixed=mesh_pixels_fixed,
        )
