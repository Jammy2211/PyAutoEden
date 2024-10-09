from typing import Tuple
from SLE_Model_Autogalaxy.SLE_Model_Profiles.SLE_Model_Light.SLE_Model_Linear.abstract import (
    LightProfileLinear,
)
from SLE_Model_Autogalaxy.SLE_Model_Profiles.SLE_Model_Light import (
    SLE_Model_Standard as lp,
)


class SersicCore(lp.SersicCore, LightProfileLinear):
    def __init__(
        self,
        centre=(0.0, 0.0),
        ell_comps=(0.0, 0.0),
        effective_radius=0.6,
        sersic_index=4.0,
        radius_break=0.01,
        gamma=0.25,
        alpha=3.0,
    ):
        """
        The elliptical cored-Sersic light profile.

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
        radius_break
            The break radius separating the inner power-law (with logarithmic slope gamma) and outer Sersic function.
        gamma
            The logarithmic power-law slope of the inner core profiles
        alpha
            Controls the sharpness of the transition between the inner core / outer Sersic profiles.
        """
        super().__init__(
            centre=centre,
            ell_comps=ell_comps,
            intensity=1.0,
            effective_radius=effective_radius,
            sersic_index=sersic_index,
            radius_break=radius_break,
            alpha=alpha,
            gamma=gamma,
        )


class SersicCoreSph(SersicCore):
    def __init__(
        self,
        centre=(0.0, 0.0),
        effective_radius=0.6,
        sersic_index=4.0,
        radius_break=0.01,
        gamma=0.25,
        alpha=3.0,
    ):
        """
        The spherical cored-Sersic light profile.

        Parameters
        ----------
        centre
            The (y,x) arc-second coordinates of the profile centre.
        effective_radius
            The circular radius containing half the light of this profile.
        sersic_index
            Controls the concentration of the profile (lower -> less concentrated, higher -> more concentrated).
        radius_break
            The break radius separating the inner power-law (with logarithmic slope gamma) and outer Sersic function.
        gamma
            The logarithmic power-law slope of the inner core profiles
        alpha
            Controls the sharpness of the transition between the inner core / outer Sersic profiles.
        """
        super().__init__(
            centre=centre,
            ell_comps=(0.0, 0.0),
            effective_radius=effective_radius,
            sersic_index=sersic_index,
            radius_break=radius_break,
            alpha=alpha,
            gamma=gamma,
        )
