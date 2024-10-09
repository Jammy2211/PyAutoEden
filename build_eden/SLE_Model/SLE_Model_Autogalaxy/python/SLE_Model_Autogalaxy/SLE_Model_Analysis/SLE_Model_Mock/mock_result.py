from __future__ import annotations
from typing import TYPE_CHECKING, Dict, List

if TYPE_CHECKING:
    from SLE_Model_Autogalaxy import SLE_Model_Mock
import SLE_Model_Autofit as af
import SLE_Model_Autogalaxy as ag


class MockResult(af.m.MockResult):
    def __init__(
        self,
        samples=None,
        instance=None,
        model=None,
        analysis=None,
        search=None,
        mask=None,
        model_image=None,
        path_galaxy_tuples=None,
        adapt_galaxy_image_path_dict=None,
        adapt_model_image=None,
        adapt_galaxy_visibilities_path_dict=None,
        adapt_model_visibilities=None,
        pixelization=None,
    ):
        super().__init__(
            samples=samples,
            instance=instance,
            model=model,
            analysis=analysis,
            search=search,
        )
        self.mask = mask
        self.adapt_galaxy_image_path_dict = adapt_galaxy_image_path_dict
        self.adapt_model_image = adapt_model_image
        self.path_galaxy_tuples = path_galaxy_tuples
        self.adapt_galaxy_visibilities_path_dict = adapt_galaxy_visibilities_path_dict
        self.adapt_model_visibilities = adapt_model_visibilities
        self.model_image = model_image
        self.unmasked_model_image = model_image
        self.pixelization = pixelization
        self.max_log_likelihood_plane = ag.Plane(galaxies=[ag.Galaxy(redshift=0.5)])

    @property
    def last(self):
        return self


class MockResults(af.ResultsCollection):
    def __init__(
        self,
        samples=None,
        instance=None,
        model=None,
        analysis=None,
        search=None,
        mask=None,
        model_image=None,
        adapt_galaxy_image_path_dict=None,
        adapt_model_image=None,
        adapt_galaxy_visibilities_path_dict=None,
        adapt_model_visibilities=None,
        pixelization=None,
    ):
        """
        A collection of results from previous searchs. Results can be obtained using an index or the name of the search
        from whence they came.
        """
        super().__init__()
        result = MockResult(
            samples=samples,
            instance=instance,
            model=model,
            analysis=analysis,
            search=search,
            mask=mask,
            model_image=model_image,
            adapt_galaxy_image_path_dict=adapt_galaxy_image_path_dict,
            adapt_model_image=adapt_model_image,
            adapt_galaxy_visibilities_path_dict=adapt_galaxy_visibilities_path_dict,
            adapt_model_visibilities=adapt_model_visibilities,
            pixelization=pixelization,
        )
        self.__result_list = [result]

    @property
    def last(self):
        """
        The result of the last search
        """
        if len(self.__result_list) > 0:
            return self.__result_list[(-1)]
        return None

    def __getitem__(self, item):
        """
        Get the result of a previous search by index

        Parameters
        ----------
        item: int
            The index of the result

        Returns
        -------
        result: Result
            The result of a previous search
        """
        return self.__result_list[item]

    def __len__(self):
        return len(self.__result_list)
