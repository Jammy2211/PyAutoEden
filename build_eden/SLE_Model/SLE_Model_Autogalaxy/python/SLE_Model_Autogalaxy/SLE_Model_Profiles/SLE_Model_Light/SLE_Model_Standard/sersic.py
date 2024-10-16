import numpy as np
from typing import Optional, Tuple
import SLE_Model_Autoarray as aa
from SLE_Model_Autogalaxy.SLE_Model_Profiles.SLE_Model_Light.abstract import (
    LightProfile,
)
from SLE_Model_Autogalaxy.SLE_Model_Profiles.SLE_Model_Light.decorators import (
    check_operated_only,
)


class AbstractSersic(LightProfile):
    def __init__(
        self,
        centre=(0.0, 0.0),
        ell_comps=(0.0, 0.0),
        intensity=0.1,
        effective_radius=0.6,
        sersic_index=4.0,
    ):
        """
        Abstract base class for elliptical Sersic light profiles.

        Parameters
        ----------
        centre
            The (y,x) arc-second coordinates of the profile centre.
        ell_comps
            The first and second ellipticity components of the elliptical coordinate system.
        intensity
            Overall intensity normalisation of the light profile (units are dimensionless and derived from the data
            the light profile's image is compared too, which is expected to be electrons per second).
        effective_radius
            The circular radius containing half the light of this light profile.
        sersic_index
            Controls the concentration of the profile (lower -> less concentrated, higher -> more concentrated).
        """
        super().__init__(centre=centre, ell_comps=ell_comps, intensity=intensity)
        self.effective_radius = effective_radius
        self.sersic_index = sersic_index

    @property
    def elliptical_effective_radius(self):
        """
        The `effective_radius` of a Sersic light profile is defined as the circular effective radius, which is the
        radius within which a circular aperture contains half the profile's total integrated light.

        For elliptical systems, this will not robustly capture the light profile's elliptical shape.

        The elliptical effective radius instead describes the major-axis radius of the ellipse containing
        half the light, and may be more appropriate for highly flattened systems like disk galaxies.
        """
        return self.effective_radius / np.sqrt(self.axis_ratio)

    @property
    def sersic_constant(self):
        """
        A parameter derived from Sersic index which ensures that effective radius contains 50% of the profile's
        total integrated light.
        """
        return (
            (
                (
                    ((2 * self.sersic_index) - (1.0 / 3.0))
                    + (4.0 / (405.0 * self.sersic_index))
                )
                + (46.0 / (25515.0 * (self.sersic_index**2)))
            )
            + (131.0 / (1148175.0 * (self.sersic_index**3)))
        ) - (2194697.0 / (30690717750.0 * (self.sersic_index**4)))

    def image_2d_via_radii_from(self, radius):
        """
        Returns the 2D image of the Sersic light profile from a grid of coordinates which are the radial distances of
        each coordinate from the its `centre`.

        Parameters
        ----------
        grid_radii
            The radial distances from the centre of the profile, for each coordinate on the grid.
        """
        return self._intensity * np.exp(
            (
                (-self.sersic_constant)
                * (((radius / self.effective_radius) ** (1.0 / self.sersic_index)) - 1)
            )
        )


class Sersic(AbstractSersic, LightProfile):
    def __init__(
        self,
        centre=(0.0, 0.0),
        ell_comps=(0.0, 0.0),
        intensity=0.1,
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
        intensity
            Overall intensity normalisation of the light profile (units are dimensionless and derived from the data
            the light profile's image is compared too, which is expected to be electrons per second).
        effective_radius
            The circular radius containing half the light of this profile.
        sersic_index
            Controls the concentration of the profile (lower -> less concentrated, higher -> more concentrated).
        """
        super().__init__(
            centre=centre,
            ell_comps=ell_comps,
            intensity=intensity,
            effective_radius=effective_radius,
            sersic_index=sersic_index,
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
        np.seterr(all="ignore")
        return np.multiply(
            self._intensity,
            np.exp(
                np.multiply(
                    (-self.sersic_constant),
                    np.add(
                        np.power(
                            np.divide(grid_radii, self.effective_radius),
                            (1.0 / self.sersic_index),
                        ),
                        (-1),
                    ),
                )
            ),
        )

    @aa.over_sample
    @aa.grid_dec.to_array
    @check_operated_only
    @aa.grid_dec.transform
    @aa.grid_dec.relocate_to_radial_minimum
    def image_2d_from(self, grid, operated_only=None, **kwargs):
        """
        Returns the Sersic light profile's 2D image from a 2D grid of Cartesian (y,x) coordinates.

        If the coordinates have not been transformed to the profile's geometry (e.g. translated to the
        profile `centre`), this is performed automatically.

        Parameters
        ----------
        grid
            The 2D (y, x) coordinates in the original reference frame of the grid.

        Returns
        -------
        image
            The image of the Sersic evaluated at every (y,x) coordinate on the transformed grid.
        """
        grid_radii = self.eccentric_radii_grid_from(grid=grid, **kwargs)
        return self.image_2d_via_radii_from(grid_radii=grid_radii, **kwargs)


class SersicSph(Sersic):
    def __init__(
        self, centre=(0.0, 0.0), intensity=0.1, effective_radius=0.6, sersic_index=4.0
    ):
        """
        The spherical Sersic light profile.

        Parameters
        ----------
        centre
            The (y,x) arc-second coordinates of the profile centre.
        intensity
            Overall intensity normalisation of the light profile (units are dimensionless and derived from the data
            the light profile's image is compared too, which is expected to be electrons per second).
        effective_radius
            The circular radius containing half the light of this profile.
        sersic_index
            Controls the concentration of the of the light profile.
        """
        super().__init__(
            centre=centre,
            ell_comps=(0.0, 0.0),
            intensity=intensity,
            effective_radius=effective_radius,
            sersic_index=sersic_index,
        )
