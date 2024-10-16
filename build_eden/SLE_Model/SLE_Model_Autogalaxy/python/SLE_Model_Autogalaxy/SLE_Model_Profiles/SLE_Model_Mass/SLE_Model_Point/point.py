import copy
import numpy as np
from typing import Tuple
import SLE_Model_Autoarray as aa
from SLE_Model_Autogalaxy.SLE_Model_Profiles.SLE_Model_Mass.SLE_Model_Abstract.abstract import (
    MassProfile,
)


class PointMass(MassProfile):
    def __init__(self, centre=(0.0, 0.0), einstein_radius=1.0):
        """
        Represents a point-mass.

        Parameters
        ----------
        centre
            The (y,x) arc-second coordinates of the profile centre.
        einstein_radius
            The arc-second Einstein radius of the point-mass.
        """
        super().__init__(centre=centre, ell_comps=(0.0, 0.0))
        self.einstein_radius = einstein_radius

    def convergence_2d_from(self, grid, **kwargs):
        squared_distances = np.square((grid[:, 0] - self.centre[0])) + np.square(
            (grid[:, 1] - self.centre[1])
        )
        central_pixel = np.argmin(squared_distances)
        convergence = np.zeros(shape=grid.shape[0])
        return convergence

    @aa.grid_dec.to_array
    def potential_2d_from(self, grid, **kwargs):
        return np.zeros(shape=grid.shape[0])

    @aa.grid_dec.to_vector_yx
    @aa.grid_dec.transform
    @aa.grid_dec.relocate_to_radial_minimum
    def deflections_yx_2d_from(self, grid, **kwargs):
        grid_radii = self.radial_grid_from(grid=grid, **kwargs)
        return self._cartesian_grid_via_radial_from(
            grid=grid, radius=((self.einstein_radius**2) / grid_radii)
        )

    @property
    def is_point_mass(self):
        return True
