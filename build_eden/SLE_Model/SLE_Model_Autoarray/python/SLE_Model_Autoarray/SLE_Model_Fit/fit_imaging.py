from typing import Dict, Optional
from SLE_Model_Autoarray.SLE_Model_Dataset.SLE_Model_Imaging.imaging import Imaging
from SLE_Model_Autoarray.SLE_Model_Fit.fit_dataset import FitDataset
from SLE_Model_Autoarray.SLE_Model_Mask.mask_2d import Mask2D
from SLE_Model_Autoarray.SLE_Model_Structures.SLE_Model_Arrays.uniform_2d import Array2D


class FitImaging(FitDataset):
    def __init__(self, dataset, use_mask_in_fit=False, profiling_dict=None):
        """
        Class to fit a masked imaging dataset.

        Parameters
        ----------
        dataset : MaskedImaging
            The masked imaging dataset that is fitted.
        model_image
            The model image the masked imaging is fitted with.
        inversion : Inversion
            If the fit uses an `Inversion` this is the instance of the object used to perform the fit. This determines
            if the `log_likelihood` or `log_evidence` is used as the `figure_of_merit`.
        use_mask_in_fit
            If `True`, masked data points are omitted from the fit. If `False` they are not (in most use cases the
            `dataset` will have been processed to remove masked points, for example the `slim` representation).

        Attributes
        -----------
        residual_map
            The residual-map of the fit (data - model_data).
        chi_squared_map
            The chi-squared-map of the fit ((data - model_data) / noise_maps ) **2.0
        chi_squared
            The overall chi-squared of the model's fit to the dataset, summed over every data point.
        reduced_chi_squared
            The reduced chi-squared of the model's fit to simulate (chi_squared / number of data points), summed over             every data point.
        noise_normalization
            The overall normalization term of the noise_map, summed over every data point.
        log_likelihood
            The overall log likelihood of the model's fit to the dataset, summed over evey data point.
        """
        super().__init__(
            dataset=dataset,
            use_mask_in_fit=use_mask_in_fit,
            profiling_dict=profiling_dict,
        )

    @property
    def imaging(self):
        return self.dataset

    @property
    def image(self):
        return self.data

    @property
    def model_image(self):
        return self.model_data

    @property
    def mask(self):
        return self.imaging.mask

    @property
    def blurred_image(self):
        raise NotImplementedError
