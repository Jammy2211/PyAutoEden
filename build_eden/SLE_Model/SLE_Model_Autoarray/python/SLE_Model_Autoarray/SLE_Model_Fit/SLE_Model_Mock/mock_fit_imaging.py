from typing import Dict, Optional
from SLE_Model_Autoarray.SLE_Model_Dataset.SLE_Model_Mock.mock_dataset import (
    MockDataset,
)
from SLE_Model_Autoarray.SLE_Model_Dataset.dataset_model import DatasetModel
from SLE_Model_Autoarray.SLE_Model_Fit.fit_imaging import FitImaging


class MockFitImaging(FitImaging):
    def __init__(
        self,
        dataset=MockDataset(),
        dataset_model=None,
        use_mask_in_fit=False,
        noise_map=None,
        model_data=None,
        inversion=None,
        blurred_image=None,
        run_time_dict=None,
    ):
        super().__init__(
            dataset=dataset,
            dataset_model=dataset_model,
            use_mask_in_fit=use_mask_in_fit,
            run_time_dict=run_time_dict,
        )
        self._noise_map = noise_map
        self._model_data = model_data
        self._inversion = inversion
        self._blurred_image = blurred_image

    @property
    def model_data(self):
        return self._model_data

    @property
    def noise_map(self):
        return self._noise_map if (self._noise_map is not None) else super().noise_map

    @property
    def inversion(self):
        return self._inversion if (self._inversion is not None) else super().inversion

    @property
    def blurred_image(self):
        return self._blurred_image if (self._blurred_image is not None) else None
