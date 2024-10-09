from typing import Tuple
from SLE_Model_Autogalaxy.SLE_Model_Profiles.SLE_Model_Light.SLE_Model_Linear.abstract import (
    LightProfileLinear,
)
from SLE_Model_Autogalaxy.SLE_Model_Profiles.SLE_Model_Light import (
    SLE_Model_Standard as lp,
)
from SLE_Model_Autogalaxy.SLE_Model_Profiles import light_and_mass_profiles as lmp


class DevVaucouleurs(lp.DevVaucouleurs, LightProfileLinear):
    def __init__(self, centre=(0.0, 0.0), ell_comps=(0.0, 0.0), effective_radius=0.6):
        """
        The elliptical DevVaucouleurs light profile.

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

    @property
    def lp_cls(self):
        return lp.DevVaucouleurs

    @property
    def lmp_cls(self):
        return lmp.DevVaucouleurs


class DevVaucouleursSph(DevVaucouleurs):
    def __init__(self, centre=(0.0, 0.0), effective_radius=0.6):
        """
        The spherical DevVaucouleurs light profile.

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
