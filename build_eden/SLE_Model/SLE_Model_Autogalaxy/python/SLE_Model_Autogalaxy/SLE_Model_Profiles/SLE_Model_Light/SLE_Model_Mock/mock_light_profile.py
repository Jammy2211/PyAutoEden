import numpy as np
from typing import Optional
import SLE_Model_Autoarray as aa
from SLE_Model_Autogalaxy.SLE_Model_Profiles.SLE_Model_Light.decorators import (
    check_operated_only,
)
import SLE_Model_Autogalaxy as ag


class MockLightProfile(ag.LightProfile):
    def __init__(
        self,
        image_2d=None,
        image_2d_value=None,
        image_2d_first_value=None,
        value=None,
        value1=None,
    ):
        super().__init__()
        self.image_2d = image_2d
        self.image_2d_value = image_2d_value
        self.image_2d_first_value = image_2d_first_value
        self.value = value
        self.value1 = value1

    @aa.grid_dec.to_array
    @check_operated_only
    def image_2d_from(self, grid, operated_only=None, **kwargs):
        if self.image_2d is not None:
            return self.image_2d
        image_2d = np.ones(shape=grid.shape[0])
        if self.image_2d_first_value is not None:
            image_2d[0] = self.image_2d_first_value
        return image_2d
