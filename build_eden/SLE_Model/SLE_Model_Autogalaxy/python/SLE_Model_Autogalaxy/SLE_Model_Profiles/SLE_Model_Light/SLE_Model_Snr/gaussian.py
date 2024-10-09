from typing import Tuple
from SLE_Model_Autogalaxy.SLE_Model_Profiles.SLE_Model_Light.SLE_Model_Snr.abstract import (
    LightProfileSNR,
)
from SLE_Model_Autogalaxy.SLE_Model_Profiles.SLE_Model_Light import (
    SLE_Model_Standard as lp,
)


class Gaussian(lp.Gaussian, LightProfileSNR):
    def __init__(
        self,
        signal_to_noise_ratio=10.0,
        centre=(0.0, 0.0),
        ell_comps=(0.0, 0.0),
        sigma=1.0,
    ):
        """
        The elliptical Gaussian light profile.

        Parameters
        ----------
        centre
            The (y,x) arc-second coordinates of the profile centre.
        ell_comps
            The first and second ellipticity components of the elliptical coordinate system.
        intensity
            Overall intensity normalisation of the light profile (units are dimensionless and derived from the data
            the light profile's image is compared too, which is expected to be electrons per second).
        sigma
            The sigma value of the Gaussian, corresponding to ~ 1 / sqrt(2 log(2)) the full width half maximum.
        """
        super().__init__(centre=centre, ell_comps=ell_comps, intensity=0.0, sigma=sigma)
        LightProfileSNR.__init__(self, signal_to_noise_ratio=signal_to_noise_ratio)


class GaussianSph(lp.GaussianSph, LightProfileSNR):
    def __init__(self, signal_to_noise_ratio=10.0, centre=(0.0, 0.0), sigma=1.0):
        """
        The spherical Gaussian light profile.

        Parameters
        ----------
        centre
            The (y,x) arc-second coordinates of the profile centre.
        intensity
            Overall intensity normalisation of the light profile (units are dimensionless and derived from the data
            the light profile's image is compared too, which is expected to be electrons per second).
        sigma
            The sigma value of the Gaussian, corresponding to ~ 1 / sqrt(2 log(2)) the full width half maximum.
        """
        super().__init__(centre=centre, intensity=0.0, sigma=sigma)
        LightProfileSNR.__init__(self, signal_to_noise_ratio=signal_to_noise_ratio)
