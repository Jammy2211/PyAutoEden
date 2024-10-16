import copy
import numpy as np
from typing import Tuple
import SLE_Model_Autoarray as aa
from SLE_Model_Autogalaxy.SLE_Model_Profiles.SLE_Model_Mass.SLE_Model_Abstract.abstract import (
    MassProfile,
)


class PowerLawBroken(MassProfile):
    def __init__(
        self,
        centre=(0.0, 0.0),
        ell_comps=(0.0, 0.0),
        einstein_radius=1.0,
        inner_slope=1.5,
        outer_slope=2.5,
        break_radius=0.01,
    ):
        """
        Ell, homoeoidal mass model with an inner_slope
        and outer_slope, continuous in density across break_radius.
        Position angle is defined to be zero on x-axis and
        +ve angle rotates the lens anticlockwise

        The grid variable is a tuple of (theta_1, theta_2), where
        each theta_1, theta_2 is itself a 2D array of the x and y
        coordinates respectively.~
        """
        super().__init__(centre=centre, ell_comps=ell_comps)
        self.einstein_radius = einstein_radius
        self.einstein_radius_elliptical = np.sqrt(self.axis_ratio) * einstein_radius
        self.break_radius = break_radius
        self.inner_slope = inner_slope
        self.outer_slope = outer_slope
        self.nu = break_radius / self.einstein_radius_elliptical
        self.dt = (2 - self.inner_slope) / (2 - self.outer_slope)
        if self.nu < 1:
            self.kB = (2 - self.inner_slope) / (
                (2 * (self.nu**2))
                * (1 + (self.dt * ((self.nu ** (self.outer_slope - 2)) - 1)))
            )
        else:
            self.kB = (2 - self.inner_slope) / (2 * (self.nu**2))

    @aa.over_sample
    @aa.grid_dec.to_array
    @aa.grid_dec.transform
    @aa.grid_dec.relocate_to_radial_minimum
    def convergence_2d_from(self, grid, **kwargs):
        """
        Returns the dimensionless density kappa=Sigma/Sigma_c (eq. 1)
        """
        radius = np.hypot((grid[:, 1] * self.axis_ratio), grid[:, 0])
        kappa_inner = self.kB * ((self.break_radius / radius) ** self.inner_slope)
        kappa_outer = self.kB * ((self.break_radius / radius) ** self.outer_slope)
        return (kappa_inner * (radius <= self.break_radius)) + (
            kappa_outer * (radius > self.break_radius)
        )

    @aa.grid_dec.to_array
    def potential_2d_from(self, grid, **kwargs):
        return np.zeros(shape=grid.shape[0])

    @aa.grid_dec.to_vector_yx
    @aa.grid_dec.transform
    @aa.grid_dec.relocate_to_radial_minimum
    def deflections_yx_2d_from(self, grid, max_terms=20, **kwargs):
        """
        Returns the complex deflection angle from eq. 18 and 19
        """
        z = grid[:, 1] + (1j * grid[:, 0])
        R = np.hypot((z.real * self.axis_ratio), z.imag)
        factors = ((2 * self.kB) * (self.break_radius**2)) / (
            (self.axis_ratio * z) * (2 - self.inner_slope)
        )
        F1 = self.hyp2f1_series(
            self.inner_slope, self.axis_ratio, R, z, max_terms=max_terms
        )
        F2 = self.hyp2f1_series(
            self.inner_slope, self.axis_ratio, self.break_radius, z, max_terms=max_terms
        )
        F3 = self.hyp2f1_series(
            self.outer_slope, self.axis_ratio, R, z, max_terms=max_terms
        )
        F4 = self.hyp2f1_series(
            self.outer_slope, self.axis_ratio, self.break_radius, z, max_terms=max_terms
        )
        inner_part = (factors * F1) * (
            (self.break_radius / R) ** (self.inner_slope - 2)
        )
        outer_part = factors * (
            F2
            + (
                self.dt
                * ((((self.break_radius / R) ** (self.outer_slope - 2)) * F3) - F4)
            )
        )
        deflections = (
            (inner_part * (R <= self.break_radius))
            + (outer_part * (R > self.break_radius))
        ).conjugate()
        return self.rotated_grid_from_reference_frame_from(
            grid=np.multiply(
                1.0, np.vstack((np.imag(deflections), np.real(deflections))).T
            )
        )

    @staticmethod
    def hyp2f1_series(t, q, r, z, max_terms=20):
        """
        Computes eq. 26 for a radius r, slope t,
        axis ratio q, and coordinates z.
        """
        q_ = (1 - (q**2)) / (q**2)
        u = 0.5 * (1 - np.sqrt((1 - (q_ * ((r / z) ** 2)))))
        a_n = 1.0
        F = np.zeros_like(z, dtype="complex64")
        for n in range(max_terms):
            F += a_n * (u**n)
            a_n *= (((2 * n) + 4) - (2 * t)) / (((2 * n) + 4) - t)
        return F


class PowerLawBrokenSph(PowerLawBroken):
    def __init__(
        self,
        centre=(0.0, 0.0),
        einstein_radius=1.0,
        inner_slope=1.5,
        outer_slope=2.5,
        break_radius=0.01,
    ):
        """
        Ell, homoeoidal mass model with an inner_slope
        and outer_slope, continuous in density across break_radius.
        Position angle is defined to be zero on x-axis and
        +ve angle rotates the lens anticlockwise

        The grid variable is a tuple of (theta_1, theta_2), where
        each theta_1, theta_2 is itself a 2D array of the x and y
        coordinates respectively.~
        """
        super().__init__(
            centre=centre,
            ell_comps=(0.0, 0.0),
            einstein_radius=einstein_radius,
            inner_slope=inner_slope,
            outer_slope=outer_slope,
            break_radius=break_radius,
        )
