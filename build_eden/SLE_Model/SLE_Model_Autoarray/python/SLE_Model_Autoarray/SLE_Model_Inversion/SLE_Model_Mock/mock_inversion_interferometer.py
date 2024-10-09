import numpy as np
from SLE_Model_Autoarray.SLE_Model_Inversion.SLE_Model_Inversion.dataset_interface import (
    DatasetInterface,
)
from SLE_Model_Autoarray.SLE_Model_Inversion.SLE_Model_Inversion.SLE_Model_Interferometer.mapping import (
    InversionInterferometerMapping,
)
from SLE_Model_Autoarray.SLE_Model_Inversion.SLE_Model_Inversion.settings import (
    SettingsInversion,
)
from SLE_Model_Autoarray.preloads import Preloads


class MockInversionInterferometer(InversionInterferometerMapping):
    def __init__(
        self,
        data=None,
        noise_map=None,
        transformer=None,
        linear_obj_list=None,
        operated_mapping_matrix=None,
        settings=SettingsInversion(),
        preloads=Preloads(),
    ):
        dataset = DatasetInterface(
            data=data, noise_map=noise_map, transformer=transformer
        )
        super().__init__(
            dataset=dataset,
            linear_obj_list=linear_obj_list,
            settings=settings,
            preloads=preloads,
        )
        self._operated_mapping_matrix = operated_mapping_matrix

    @property
    def operated_mapping_matrix(self):
        if self._operated_mapping_matrix is None:
            return super().operated_mapping_matrix
        return self._operated_mapping_matrix
