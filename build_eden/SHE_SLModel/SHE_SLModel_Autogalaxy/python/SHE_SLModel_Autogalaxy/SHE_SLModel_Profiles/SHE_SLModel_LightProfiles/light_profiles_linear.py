import numpy as np
from typing import Dict, Optional, Tuple
import SHE_SLModel_Autoarray as aa
from SHE_SLModel_Autogalaxy.SHE_SLModel_Profiles.SHE_SLModel_LightProfiles import (
    light_profiles as lp,
)


class LightProfileLinear(aa.LinearObjFunc):
    def __init__(
        self, light_profile, grid, blurring_grid, convolver, profiling_dict=None
    ):
        super().__init__(grid=grid, profiling_dict=profiling_dict)
        self.light_profile = light_profile
        self.blurring_grid = blurring_grid
        self.convolver = convolver

    @property
    def image_2d_from(self):
        return self.light_profile.image_2d_from

    @property
    def pixels(self):
        return 1

    @property
    def blurred_mapping_matrix_override(self):
        """
        Returns the `blurred_mapping_matrix` of the light profile, which is the image of the light profile within the
        mask blurred with the PSF via a 2D convolution operation. This convolution includes evaluating the flux in the
        light profile which is outside the masked region but blurs into it due to the size of the PSF.

        The `LinearEqn` objects that perform the inversion in PyAutoArray usually combine the `mapping_matrix` of each
        linear object with the `Convolver` operator to perform a 2D convolution and compute
        the `blurred_mapping_matrix`.

        However, this is not possible for a light profile beause of how flux outside the masked region blurs into the
        masked region; this flux is outside the region defined by the `mapping_matrix`. By using the
        ``blurred_mapping_matrix_override` this class bypass the `mapping_matrix` calculation and directly passes
        the inversion the `blurred_mapping_matrix`.

        Returns
        -------
        A blurred mapping matrix of dimensions (total_mask_pixels, 1) which overrides the mapping matrix calculations
        performed in the linear equation solvers.
        """
        blurred_image = self.light_profile.blurred_image_2d_via_convolver_from(
            grid=self.grid, convolver=self.convolver, blurring_grid=self.blurring_grid
        )
        blurred_mapping_matrix = np.zeros((self.grid.shape_slim, 1))
        blurred_mapping_matrix[:, 0] = blurred_image
        return blurred_mapping_matrix


class EllSersic(lp.EllSersic):
    def __init__(
        self,
        centre=(0.0, 0.0),
        elliptical_comps=(0.0, 0.0),
        effective_radius=0.6,
        sersic_index=4.0,
    ):
        """
        The elliptical Sersic light profile.

        See `autogalaxy.profiles.light_profiles.light_profiles.LightProfile` for a description of light profile objects.

        Parameters
        ----------
        centre
            The (y,x) arc-second coordinates of the profile centre.
        elliptical_comps
            The first and second ellipticity components of the elliptical coordinate system, (see the module
            `autogalaxy -> convert.py` for the convention).
        effective_radius
            The circular radius containing half the light of this profile.
        sersic_index
            Controls the concentration of the profile (lower -> less concentrated, higher -> more concentrated).
        """
        super().__init__(
            centre=centre,
            elliptical_comps=elliptical_comps,
            intensity=1.0,
            effective_radius=effective_radius,
            sersic_index=sersic_index,
        )
