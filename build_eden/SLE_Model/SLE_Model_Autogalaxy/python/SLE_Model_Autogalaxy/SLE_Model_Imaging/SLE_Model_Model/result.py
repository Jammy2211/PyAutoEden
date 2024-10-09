from typing import List
import SLE_Model_Autoarray as aa
from SLE_Model_Autogalaxy.SLE_Model_Galaxy.galaxy import Galaxy
from SLE_Model_Autogalaxy.SLE_Model_Analysis.result import ResultDataset
from SLE_Model_Autogalaxy.SLE_Model_Imaging.fit_imaging import FitImaging


class ResultImaging(ResultDataset):
    @property
    def max_log_likelihood_fit(self):
        """
        An instance of a `FitImaging` corresponding to the maximum log likelihood model inferred by the non-linear
        search.
        """
        return self.analysis.fit_from(instance=self.instance)

    @property
    def max_log_likelihood_galaxies(self):
        """
        An instance of galaxies corresponding to the maximum log likelihood model inferred by the non-linear search.

        The galaxies list is computed from the `max_log_likelihood_fit`, as this ensures that all linear light profiles
        are converted to normal light profiles with their `intensity` values updated.
        """
        return (
            self.max_log_likelihood_fit.model_obj_linear_light_profiles_to_light_profiles
        )

    @property
    def unmasked_model_image(self):
        """
        The model image of the maximum log likelihood model, creating without using a mask.
        """
        return self.max_log_likelihood_fit.unmasked_blurred_image

    @property
    def unmasked_model_image_of_galaxies(self):
        """
        A list of the model image of every galaxy in the maximum log likelihood model, whereas all images are created
        without using a mask.
        """
        return self.max_log_likelihood_fit.unmasked_blurred_image_of_galaxies_list
