from typing import Tuple
from SLE_Model_Autogalaxy.SLE_Model_Profiles.SLE_Model_Light.SLE_Model_Linear.abstract import (
    LightProfileLinear,
)
from SLE_Model_Autogalaxy.SLE_Model_Profiles.SLE_Model_Light import (
    SLE_Model_Standard as lp,
)


class Sersic(lp.Sersic, LightProfileLinear):
    def __init__(
        self,
        centre=(0.0, 0.0),
        ell_comps=(0.0, 0.0),
        effective_radius=0.6,
        sersic_index=4.0,
    ):
        """
        The elliptical Sersic light profile.

        Parameters
        ----------
        centre
            The (y,x) arc-second coordinates of the profile centre.
        ell_comps
            The first and second ellipticity components of the elliptical coordinate system.
        effective_radius
            The circular radius containing half the light of this profile.
        sersic_index
            Controls the concentration of the profile (lower -> less concentrated, higher -> more concentrated).
        """
        super().__init__(
            centre=centre,
            ell_comps=ell_comps,
            intensity=1.0,
            effective_radius=effective_radius,
            sersic_index=sersic_index,
        )


class SersicSph(Sersic):
    def __init__(self, centre=(0.0, 0.0), effective_radius=0.6, sersic_index=4.0):
        """
        The spherical Sersic light profile.

        Parameters
        ----------
        centre
            The (y,x) arc-second coordinates of the profile centre.
        effective_radius
            The circular radius containing half the light of this profile.
        sersic_index
            Controls the concentration of the profile (lower -> less concentrated, higher -> more concentrated).
        """
        super().__init__(
            centre=centre,
            ell_comps=(0.0, 0.0),
            effective_radius=effective_radius,
            sersic_index=sersic_index,
        )
