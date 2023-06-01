import numpy as np
from typing import Dict, List, Optional
import SLE_Model_Autoarray as aa
from SLE_Model_Autogalaxy.SLE_Model_Profiles.SLE_Model_Light.abstract import (
    LightProfile,
)
from SLE_Model_Autogalaxy.SLE_Model_Profiles.SLE_Model_Light import (
    SLE_Model_Linear as lp_linear,
)


class Basis(LightProfile):
    def __init__(self, light_profile_list, regularization=None):
        super().__init__(
            centre=light_profile_list[0].centre,
            ell_comps=light_profile_list[0].ell_comps,
        )
        self.light_profile_list = light_profile_list
        self.regularization = regularization

    def image_2d_from(self, grid, operated_only=None):
        return sum(self.image_2d_list_from(grid=grid, operated_only=operated_only))

    def image_2d_list_from(self, grid, operated_only=None):
        return [
            (
                light_profile.image_2d_from(grid=grid, operated_only=operated_only)
                if (not isinstance(light_profile, lp_linear.LightProfileLinear))
                else np.zeros((grid.shape[0],))
            )
            for light_profile in self.light_profile_list
        ]

    def lp_instance_from(self, linear_light_profile_intensity_dict):
        light_profile_list = []
        for light_profile in self.light_profile_list:
            if isinstance(light_profile, lp_linear.LightProfileLinear):
                light_profile = light_profile.lp_instance_from(
                    linear_light_profile_intensity_dict=linear_light_profile_intensity_dict
                )
            light_profile_list.append(light_profile)
        return Basis(
            light_profile_list=light_profile_list, regularization=self.regularization
        )
