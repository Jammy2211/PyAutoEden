import numpy as np
from typing import Tuple
import SLE_Model_Autoarray as aa
from SLE_Model_Autogalaxy.SLE_Model_Profiles.SLE_Model_Mass.SLE_Model_Total.power_law import (
    PowerLaw,
)


def psi_from(grid, axis_ratio, core_radius):
    """
    Returns the $\\Psi$ term in expressions for the calculation of the deflection of an elliptical isothermal mass
    distribution. This is used in the `Isothermal` and `Chameleon` `MassProfile`'s.

    The expression for Psi is:

    $\\Psi = \\sqrt(q^2(s^2 + x^2) + y^2)$

    Parameters
    ----------
    grid
        The (y,x) coordinates of the grid, in an arrays of shape (total_coordinates, 2)
    axis_ratio
            Ratio of profiles ellipse's minor and major axes (b/a)
    core_radius
        The radius of the inner core

    Returns
    -------
    float
        The value of the Psi term.

    """
    return np.sqrt(
        np.add(
            np.multiply(
                (axis_ratio**2.0), np.add(np.square(grid[:, 1]), (core_radius**2.0))
            ),
            np.square(grid[:, 0]),
        )
    )


class Isothermal(PowerLaw):
    def __init__(self, centre=(0.0, 0.0), ell_comps=(0.0, 0.0), einstein_radius=1.0):
        """
        Represents an elliptical isothermal density distribution, which is equivalent to the elliptical power-law
        density distribution for the value slope: float = 2.0

        Parameters
        ----------
        centre
            The (y,x) arc-second coordinates of the profile centre.
        ell_comps
            The first and second ellipticity components of the elliptical coordinate system.
        einstein_radius
            The arc-second Einstein radius.
        """
        super().__init__(
            centre=centre,
            ell_comps=ell_comps,
            einstein_radius=einstein_radius,
            slope=2.0,
        )

    @property
    def axis_ratio(self):
        axis_ratio = super().axis_ratio
        return min(axis_ratio, 0.99999)

    @aa.grid_dec.grid_2d_to_vector_yx
    @aa.grid_dec.grid_2d_to_structure
    @aa.grid_dec.transform
    @aa.grid_dec.relocate_to_radial_minimum
    def deflections_yx_2d_from(self, grid):
        """
        Calculate the deflection angles on a grid of (y,x) arc-second coordinates.

        For coordinates (0.0, 0.0) the analytic calculation of the deflection angle gives a NaN. Therefore,
        coordinates at (0.0, 0.0) are shifted slightly to (1.0e-8, 1.0e-8).

        Parameters
        ----------
        grid
            The grid of (y,x) arc-second coordinates the deflection angles are computed on.
        """
        factor = ((2.0 * self.einstein_radius_rescaled) * self.axis_ratio) / np.sqrt(
            (1 - (self.axis_ratio**2))
        )
        psi = psi_from(grid=grid, axis_ratio=self.axis_ratio, core_radius=0.0)
        deflection_y = np.arctanh(
            np.divide(
                np.multiply(np.sqrt((1 - (self.axis_ratio**2))), grid[:, 0]), psi
            )
        )
        deflection_x = np.arctan(
            np.divide(
                np.multiply(np.sqrt((1 - (self.axis_ratio**2))), grid[:, 1]), psi
            )
        )
        return self.rotated_grid_from_reference_frame_from(
            grid=np.multiply(factor, np.vstack((deflection_y, deflection_x)).T)
        )

    @aa.grid_dec.grid_2d_to_structure
    @aa.grid_dec.transform
    @aa.grid_dec.relocate_to_radial_minimum
    def shear_2d_from(self, grid):
        """
        Calculate the (gamma_y, gamma_x) shear vector field on a grid of (y,x) arc-second coordinates.

        Parameters
        ----------
        grid
            The grid of (y,x) arc-second coordinates the deflection angles are computed on.
        """
        convergence = self.convergence_2d_from(grid=grid)
        shear_y = ((-2) * convergence) * np.divide(
            (grid[:, 1] * grid[:, 0]), ((grid[:, 1] ** 2) + (grid[:, 0] ** 2))
        )
        shear_x = (-convergence) * np.divide(
            ((grid[:, 1] ** 2) - (grid[:, 0] ** 2)),
            ((grid[:, 1] ** 2) + (grid[:, 0] ** 2)),
        )
        shear_field = self.rotated_grid_from_reference_frame_from(
            grid=np.vstack((shear_y, shear_x)).T
        )
        return aa.VectorYX2DIrregular(values=shear_field, grid=grid)


class IsothermalSph(Isothermal):
    def __init__(self, centre=(0.0, 0.0), einstein_radius=1.0):
        """
        Represents a spherical isothermal density distribution, which is equivalent to the spherical power-law
        density distribution for the value slope: float = 2.0

        Parameters
        ----------
        centre
            The (y,x) arc-second coordinates of the profile centre.
        einstein_radius
            The arc-second Einstein radius.
        """
        super().__init__(
            centre=centre, ell_comps=(0.0, 0.0), einstein_radius=einstein_radius
        )

    @property
    def axis_ratio(self):
        return 1.0

    @aa.grid_dec.grid_2d_to_structure
    @aa.grid_dec.transform
    @aa.grid_dec.relocate_to_radial_minimum
    def potential_2d_from(self, grid):
        """
        Calculate the potential on a grid of (y,x) arc-second coordinates.

        Parameters
        ----------
        grid
            The grid of (y,x) arc-second coordinates the deflection angles are computed on.
        """
        eta = self.elliptical_radii_grid_from(grid)
        return (2.0 * self.einstein_radius_rescaled) * eta

    @aa.grid_dec.grid_2d_to_vector_yx
    @aa.grid_dec.grid_2d_to_structure
    @aa.grid_dec.transform
    @aa.grid_dec.relocate_to_radial_minimum
    def deflections_yx_2d_from(self, grid):
        """
        Calculate the deflection angles on a grid of (y,x) arc-second coordinates.

        Parameters
        ----------
        grid
            The grid of (y,x) arc-second coordinates the deflection angles are computed on.
        """
        return self._cartesian_grid_via_radial_from(
            grid=grid,
            radius=np.full(grid.shape[0], (2.0 * self.einstein_radius_rescaled)),
        )