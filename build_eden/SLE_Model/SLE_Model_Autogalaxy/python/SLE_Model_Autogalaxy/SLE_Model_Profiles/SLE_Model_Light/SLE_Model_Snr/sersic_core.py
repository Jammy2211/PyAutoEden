from typing import Tuple
from SLE_Model_Autogalaxy.SLE_Model_Profiles.SLE_Model_Light.SLE_Model_Snr.abstract import (
    LightProfileSNR,
)
from SLE_Model_Autogalaxy.SLE_Model_Profiles.SLE_Model_Light import (
    SLE_Model_Standard as lp,
)


class SersicCore(lp.SersicCore, LightProfileSNR):
    def __init__(
        self,
        signal_to_noise_ratio=10.0,
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

        Instead of an `intensity` a `signal_to_noise_ratio` is input which sets the signal to noise of the brightest
        pixel of the profile's image when used to simulate imaging data.

        Parameters
        ----------
        signal_to_noise_ratio
            The signal to noise of the light profile when it is used to simulate strong lens imaging.
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
            effective_radius=effective_radius,
            sersic_index=sersic_index,
            radius_break=radius_break,
            intensity=0.0,
            alpha=alpha,
            gamma=gamma,
        )
        LightProfileSNR.__init__(self, signal_to_noise_ratio=signal_to_noise_ratio)
