import numpy as np
from typing import Tuple
from SLE_Model_Autogalaxy.SLE_Model_Profiles.SLE_Model_Light.SLE_Model_Standard.sersic import (
    Sersic,
)


class SersicCore(Sersic):
    def __init__(
        self,
        centre=(0.0, 0.0),
        ell_comps=(0.0, 0.0),
        effective_radius=0.6,
        sersic_index=4.0,
        radius_break=0.025,
        intensity=0.05,
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
        intensity
            The intensity at the break radius.
        gamma
            The logarithmic power-law slope of the inner core profiles
        alpha
            Controls the sharpness of the transition between the inner core / outer Sersic profiles.
        """
        super().__init__(
            centre=centre,
            ell_comps=ell_comps,
            intensity=intensity,
            effective_radius=effective_radius,
            sersic_index=sersic_index,
        )
        self.radius_break = radius_break
        self.intensity = intensity
        self.alpha = alpha
        self.gamma = gamma

    @property
    def intensity_prime(self):
        """
        Overall intensity normalisation in the rescaled cored Sersic light profile.

        Like the `intensity` parameter, the units of `intensity_prime` are dimensionless and derived from the data
        the light profile's image is compared too, which are expected to be electrons per second.
        """
        return (self._intensity * (2.0 ** ((-self.gamma) / self.alpha))) * np.exp(
            (
                self.sersic_constant
                * (
                    (
                        ((2.0 ** (1.0 / self.alpha)) * self.radius_break)
                        / self.effective_radius
                    )
                    ** (1.0 / self.sersic_index)
                )
            )
        )

    def image_2d_via_radii_from(self, grid_radii, **kwargs):
        """
        Returns the 2D image of the Sersic light profile from a grid of coordinates which are the radial distances of
        each coordinate from the its `centre`.

        Parameters
        ----------
        grid_radii
            The radial distances from the centre of the profile, for each coordinate on the grid.
        """
        return np.multiply(
            np.multiply(
                self.intensity_prime,
                np.power(
                    np.add(
                        1,
                        np.power(np.divide(self.radius_break, grid_radii), self.alpha),
                    ),
                    (self.gamma / self.alpha),
                ),
            ),
            np.exp(
                np.multiply(
                    (-self.sersic_constant),
                    np.power(
                        np.divide(
                            np.add(
                                np.power(grid_radii, self.alpha),
                                (self.radius_break**self.alpha),
                            ),
                            (self.effective_radius**self.alpha),
                        ),
                        (1.0 / (self.alpha * self.sersic_index)),
                    ),
                )
            ),
        )


class SersicCoreSph(SersicCore):
    def __init__(
        self,
        centre=(0.0, 0.0),
        effective_radius=0.6,
        sersic_index=4.0,
        radius_break=0.01,
        intensity=0.05,
        gamma=0.25,
        alpha=3.0,
    ):
        """
        The elliptical cored-Sersic light profile.

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
        intensity
            The intensity at the break radius.
        gamma
            The logarithmic power-law slope of the inner core profiles
        alpha :
            Controls the sharpness of the transition between the inner core / outer Sersic profiles.
        """
        super().__init__(
            centre=centre,
            ell_comps=(0.0, 0.0),
            effective_radius=effective_radius,
            sersic_index=sersic_index,
            radius_break=radius_break,
            intensity=intensity,
            gamma=gamma,
            alpha=alpha,
        )
        self.radius_break = radius_break
        self.intensity = intensity
        self.alpha = alpha
        self.gamma = gamma
