from typing import Tuple
from SLE_Model_Autogalaxy.SLE_Model_Profiles.SLE_Model_Light.SLE_Model_Linear.abstract import (
    LightProfileLinear,
)
from SLE_Model_Autogalaxy.SLE_Model_Profiles.SLE_Model_Light import (
    SLE_Model_Standard as lp,
)


class Exponential(lp.Exponential, LightProfileLinear):
    def __init__(self, centre=(0.0, 0.0), ell_comps=(0.0, 0.0), effective_radius=0.6):
        """
        The elliptical Exponential light profile.

        Parameters
        ----------
        centre
            The (y,x) arc-second coordinates of the profile centre.
        ell_comps
            The first and second ellipticity components of the elliptical coordinate system.
        effective_radius
            The circular radius containing half the light of this profile.
        """
        super().__init__(
            centre=centre,
            ell_comps=ell_comps,
            intensity=1.0,
            effective_radius=effective_radius,
        )


class ExponentialSph(Exponential):
    def __init__(self, centre=(0.0, 0.0), effective_radius=0.6):
        """
        The spherical Exponential light profile.

        Parameters
        ----------
        centre
            The (y,x) arc-second coordinates of the profile centre.
        effective_radius
            The circular radius containing half the light of this profile.
        """
        super().__init__(
            centre=centre, ell_comps=(0.0, 0.0), effective_radius=effective_radius
        )
