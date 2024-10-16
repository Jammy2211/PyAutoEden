import copy
import numpy as np
from typing import Tuple
import SLE_Model_Autoarray as aa
from SLE_Model_Autogalaxy.SLE_Model_Profiles.SLE_Model_Mass.SLE_Model_Abstract.abstract import (
    MassProfile,
)
from SLE_Model_Autogalaxy.SLE_Model_Profiles.SLE_Model_Mass.SLE_Model_Stellar.abstract import (
    StellarProfile,
)
from SLE_Model_Autogalaxy.SLE_Model_Profiles.SLE_Model_Mass.SLE_Model_Total.isothermal import (
    psi_from,
)


class Chameleon(MassProfile, StellarProfile):
    def __init__(
        self,
        centre=(0.0, 0.0),
        ell_comps=(0.0, 0.0),
        intensity=0.1,
        core_radius_0=0.01,
        core_radius_1=0.02,
        mass_to_light_ratio=1.0,
    ):
        """
        The elliptical Chamelon mass profile.

        Parameters
        ----------
        centre
            The (y,x) arc-second coordinates of the profile centre.
        ell_comps
            The first and second ellipticity components of the elliptical coordinate system.
        intensity
            Overall intensity normalisation of the light profile (units are dimensionless and derived from the data
            the light profile's image is compared too, which is expected to be electrons per second).
        core_radius_0 : the core size of the first elliptical cored Isothermal profile.
        core_radius_1 : core_radius_0 + core_radius_1 is the core size of the second elliptical cored Isothermal profile.
            We use core_radius_1 here is to avoid negative values.

        Profile form:
            mass_to_light_ratio * intensity *                (1.0 / Sqrt(x^2 + (y/q)^2 + core_radius_0^2) - 1.0 / Sqrt(x^2 + (y/q)^2 + (core_radius_0 + core_radius_1)**2.0))
        """
        super(Chameleon, self).__init__(centre=centre, ell_comps=ell_comps)
        super(MassProfile, self).__init__(centre=centre, ell_comps=ell_comps)
        self.mass_to_light_ratio = mass_to_light_ratio
        self.intensity = intensity
        self.core_radius_0 = core_radius_0
        self.core_radius_1 = core_radius_1

    def deflections_yx_2d_from(self, grid, **kwargs):
        return self.deflections_2d_via_analytic_from(grid=grid, **kwargs)

    @aa.grid_dec.to_vector_yx
    @aa.grid_dec.transform
    @aa.grid_dec.relocate_to_radial_minimum
    def deflections_2d_via_analytic_from(self, grid, **kwargs):
        """
        Calculate the deflection angles at a given set of arc-second gridded coordinates.
        Following Eq. (15) and (16), but the parameters are slightly different.

        Parameters
        ----------
        grid
            The grid of (y,x) arc-second coordinates the deflection angles are computed on.

        """
        factor = (
            (
                ((2.0 * self.mass_to_light_ratio) * self.intensity)
                / (1 + self.axis_ratio)
            )
            * self.axis_ratio
        ) / np.sqrt((1.0 - (self.axis_ratio**2.0)))
        core_radius_0 = np.sqrt(
            ((4.0 * (self.core_radius_0**2.0)) / ((1.0 + self.axis_ratio) ** 2))
        )
        core_radius_1 = np.sqrt(
            ((4.0 * (self.core_radius_1**2.0)) / ((1.0 + self.axis_ratio) ** 2))
        )
        psi0 = psi_from(
            grid=grid, axis_ratio=self.axis_ratio, core_radius=core_radius_0
        )
        psi1 = psi_from(
            grid=grid, axis_ratio=self.axis_ratio, core_radius=core_radius_1
        )
        deflection_y0 = np.arctanh(
            np.divide(
                np.multiply(np.sqrt((1.0 - (self.axis_ratio**2.0))), grid[:, 0]),
                np.add(psi0, ((self.axis_ratio**2.0) * core_radius_0)),
            )
        )
        deflection_x0 = np.arctan(
            np.divide(
                np.multiply(np.sqrt((1.0 - (self.axis_ratio**2.0))), grid[:, 1]),
                np.add(psi0, core_radius_0),
            )
        )
        deflection_y1 = np.arctanh(
            np.divide(
                np.multiply(np.sqrt((1.0 - (self.axis_ratio**2.0))), grid[:, 0]),
                np.add(psi1, ((self.axis_ratio**2.0) * core_radius_1)),
            )
        )
        deflection_x1 = np.arctan(
            np.divide(
                np.multiply(np.sqrt((1.0 - (self.axis_ratio**2.0))), grid[:, 1]),
                np.add(psi1, core_radius_1),
            )
        )
        deflection_y = np.subtract(deflection_y0, deflection_y1)
        deflection_x = np.subtract(deflection_x0, deflection_x1)
        return self.rotated_grid_from_reference_frame_from(
            np.multiply(factor, np.vstack((deflection_y, deflection_x)).T)
        )

    @aa.over_sample
    @aa.grid_dec.to_array
    @aa.grid_dec.transform
    @aa.grid_dec.relocate_to_radial_minimum
    def convergence_2d_from(self, grid, **kwargs):
        """Calculate the projected convergence at a given set of arc-second gridded coordinates.
        Parameters
        ----------
        grid
            The grid of (y,x) arc-second coordinates the convergence is computed on.
        """
        return self.convergence_func(
            self.elliptical_radii_grid_from(grid=grid, **kwargs)
        )

    def convergence_func(self, grid_radius):
        return self.mass_to_light_ratio * self.image_2d_via_radii_from(grid_radius)

    @aa.grid_dec.to_array
    def potential_2d_from(self, grid, **kwargs):
        return np.zeros(shape=grid.shape[0])

    def image_2d_via_radii_from(self, grid_radii):
        """Calculate the intensity of the Chamelon light profile on a grid of radial coordinates.

        Parameters
        ----------
        grid_radii
            The radial distance from the centre of the profile. for each coordinate on the grid.
        """
        axis_ratio_factor = (1.0 + self.axis_ratio) ** 2.0
        return np.multiply(
            (self.intensity / (1 + self.axis_ratio)),
            np.add(
                np.divide(
                    1.0,
                    np.sqrt(
                        np.add(
                            np.square(grid_radii),
                            ((4.0 * (self.core_radius_0**2.0)) / axis_ratio_factor),
                        )
                    ),
                ),
                (
                    -np.divide(
                        1.0,
                        np.sqrt(
                            np.add(
                                np.square(grid_radii),
                                (
                                    (4.0 * (self.core_radius_1**2.0))
                                    / axis_ratio_factor
                                ),
                            )
                        ),
                    )
                ),
            ),
        )

    @property
    def axis_ratio(self):
        axis_ratio = super().axis_ratio
        return axis_ratio if (axis_ratio < 0.99999) else 0.99999


class ChameleonSph(Chameleon):
    def __init__(
        self,
        centre=(0.0, 0.0),
        intensity=0.1,
        core_radius_0=0.01,
        core_radius_1=0.02,
        mass_to_light_ratio=1.0,
    ):
        """
        The spherica; Chameleon mass profile.

        Profile form:
            mass_to_light_ratio * intensity *                (1.0 / Sqrt(x^2 + (y/q)^2 + core_radius_0^2) - 1.0 / Sqrt(x^2 + (y/q)^2 + (core_radius_0 + core_radius_1)**2.0))

        Parameters
        ----------
        centre
            The (y,x) arc-second coordinates of the profile centre.
        ell_comps
            The first and second ellipticity components of the elliptical coordinate system.
        intensity
            Overall intensity normalisation of the light profile (units are dimensionless and derived from the data
            the light profile's image is compared too, which is expected to be electrons per second).
        core_radius_0 : the core size of the first elliptical cored Isothermal profile.
        core_radius_1 : core_radius_0 + core_radius_1 is the core size of the second elliptical cored Isothermal profile.
            We use core_radius_1 here is to avoid negative values.
        """
        super().__init__(
            centre=centre,
            ell_comps=(0.0, 0.0),
            intensity=intensity,
            core_radius_0=core_radius_0,
            core_radius_1=core_radius_1,
            mass_to_light_ratio=mass_to_light_ratio,
        )
