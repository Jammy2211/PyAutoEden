import numpy as np
from typing import Dict, Optional
from SLE_Model_Autoarray.SLE_Model_Dataset.SLE_Model_Interferometer.dataset import (
    Interferometer,
)
from SLE_Model_Autoarray.SLE_Model_Dataset.dataset_model import DatasetModel
from SLE_Model_Autoarray.SLE_Model_Structures.SLE_Model_Arrays.uniform_2d import Array2D
from SLE_Model_Autoarray.SLE_Model_Structures.visibilities import Visibilities
from SLE_Model_Autoarray.SLE_Model_Fit.fit_dataset import FitDataset
from SLE_Model_Autoarray.SLE_Model_Fit import fit_util
from SLE_Model_Autoarray import type as ty


class FitInterferometer(FitDataset):
    def __init__(
        self, dataset, dataset_model=None, use_mask_in_fit=False, run_time_dict=None
    ):
        """
        Class to fit a masked interferometer dataset.

        Parameters
        ----------
        dataset : MaskedInterferometer
            The masked interferometer dataset that is fitted.
        dataset_model
            Attributes which allow for parts of a dataset to be treated as a model (e.g. the background sky level).
        model_data : Visibilities
            The model visibilities the masked imaging is fitted with.
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
            The chi-squared-map of the fit ((data - model_data) / noise_map ) **2.0
        chi_squared
            The overall chi-squared of the model's fit to the dataset, summed over every data point.
        reduced_chi_squared
            The reduced chi-squared of the model's fit to simulate (chi_squared / number of data points), summed over
            every data point.
        noise_normalization
            The overall normalization term of the noise_map, summed over every data point.
        log_likelihood
            The overall log likelihood of the model's fit to the dataset, summed over evey data point.
        """
        super().__init__(
            dataset=dataset,
            dataset_model=dataset_model,
            use_mask_in_fit=use_mask_in_fit,
            run_time_dict=run_time_dict,
        )

    @property
    def mask(self):
        return np.full(shape=self.data.shape, fill_value=False)

    @property
    def transformer(self):
        return self.dataset.transformer

    @property
    def normalized_residual_map(self):
        """
        Returns the normalized residual-map between the masked dataset and model data, where:

        Normalized_Residual = (Data - Model_Data) / Noise
        """
        return fit_util.normalized_residual_map_complex_from(
            residual_map=self.residual_map, noise_map=self.noise_map
        )

    @property
    def chi_squared_map(self):
        """
        Returns the chi-squared-map between the residual-map and noise-map, where:

        Chi_Squared = ((Residuals) / (Noise)) ** 2.0 = ((Data - Model)**2.0)/(Variances)
        """
        return fit_util.chi_squared_map_complex_from(
            residual_map=self.residual_map, noise_map=self.noise_map
        )

    @property
    def signal_to_noise_map(self):
        """
        The signal-to-noise_map of the dataset and noise-map which are fitted."""
        signal_to_noise_map_real = self.data.real / self.noise_map.real
        signal_to_noise_map_real[(signal_to_noise_map_real < 0)] = 0.0
        signal_to_noise_map_imag = self.data.imag / self.noise_map.imag
        signal_to_noise_map_imag[(signal_to_noise_map_imag < 0)] = 0.0
        return signal_to_noise_map_real + (1j * signal_to_noise_map_imag)

    @property
    def chi_squared(self):
        """
        Returns the chi-squared terms of the model data's fit to an dataset, by summing the chi-squared-map.
        """
        return fit_util.chi_squared_complex_from(chi_squared_map=self.chi_squared_map)

    @property
    def noise_normalization(self):
        """
        Returns the noise-map normalization term of the noise-map, summing the noise_map value in every pixel as:

        [Noise_Term] = sum(log(2*pi*[Noise]**2.0))
        """
        return fit_util.noise_normalization_complex_from(noise_map=self.noise_map)

    @property
    def dirty_image(self):
        return self.transformer.image_from(visibilities=self.data)

    @property
    def dirty_noise_map(self):
        return self.transformer.image_from(visibilities=self.noise_map)

    @property
    def dirty_signal_to_noise_map(self):
        return self.transformer.image_from(visibilities=self.signal_to_noise_map)

    @property
    def dirty_model_image(self):
        return self.transformer.image_from(visibilities=self.model_data)

    @property
    def dirty_residual_map(self):
        return self.transformer.image_from(visibilities=self.residual_map)

    @property
    def dirty_normalized_residual_map(self):
        return self.transformer.image_from(visibilities=self.normalized_residual_map)

    @property
    def dirty_chi_squared_map(self):
        return self.transformer.image_from(visibilities=self.chi_squared_map)
