from typing import Tuple
from SLE_Model_Autogalaxy.SLE_Model_Profiles.SLE_Model_Light.SLE_Model_Linear.abstract import (
    LightProfileLinear,
)
from SLE_Model_Autogalaxy.SLE_Model_Profiles.SLE_Model_Light import (
    SLE_Model_Standard as lp,
)
from SLE_Model_Autogalaxy.SLE_Model_Profiles import light_and_mass_profiles as lmp


class Gaussian(lp.Gaussian, LightProfileLinear):
    def __init__(self, centre=(0.0, 0.0), ell_comps=(0.0, 0.0), sigma=1.0):
        """
        The elliptical Gaussian light profile.

        Parameters
        ----------
        centre
            The (y,x) arc-second coordinates of the profile centre.
        ell_comps
            The first and second ellipticity components of the elliptical coordinate system.
        sigma
            The sigma value of the Gaussian, corresponding to ~ 1 / sqrt(2 log(2)) the full width half maximum.
        """
        super().__init__(centre=centre, ell_comps=ell_comps, intensity=1.0, sigma=sigma)

    @property
    def lp_cls(self):
        return lp.Gaussian

    @property
    def lmp_cls(self):
        return lmp.Gaussian


class GaussianSph(Gaussian):
    def __init__(self, centre=(0.0, 0.0), sigma=1.0):
        """
        The spherical Gaussian light profile.

        Parameters
        ----------
        centre
            The (y,x) arc-second coordinates of the profile centre.
        sigma
            The sigma value of the Gaussian, corresponding to ~ 1 / sqrt(2 log(2)) the full width half maximum.
        """
        super().__init__(centre=centre, ell_comps=(0.0, 0.0), sigma=sigma)

    @property
    def lp_cls(self):
        return lp.GaussianSph
