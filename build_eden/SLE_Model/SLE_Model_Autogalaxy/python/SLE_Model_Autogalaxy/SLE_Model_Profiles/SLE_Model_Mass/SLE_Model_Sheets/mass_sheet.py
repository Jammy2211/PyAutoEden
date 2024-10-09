import numpy as np
from typing import Tuple
import SLE_Model_Autoarray as aa
from SLE_Model_Autogalaxy.SLE_Model_Profiles.SLE_Model_Mass.SLE_Model_Abstract.abstract import (
    MassProfile,
)


class MassSheet(MassProfile):
    def __init__(self, centre=(0.0, 0.0), kappa=0.0):
        """
        Represents a mass-sheet

        Parameters
        ----------
        centre
            The (y,x) arc-second coordinates of the profile centre.
        kappa
            The magnitude of the convergence of the mass-sheet.
        """
        super().__init__(centre=centre, ell_comps=(0.0, 0.0))
        self.kappa = kappa

    def convergence_func(self, grid_radius):
        return 0.0

    @aa.grid_dec.to_array
    def convergence_2d_from(self, grid, **kwargs):
        return np.full(shape=grid.shape[0], fill_value=self.kappa)

    @aa.grid_dec.to_array
    def potential_2d_from(self, grid, **kwargs):
        return np.zeros(shape=grid.shape[0])

    @aa.grid_dec.to_vector_yx
    @aa.grid_dec.transform
    @aa.grid_dec.relocate_to_radial_minimum
    def deflections_yx_2d_from(self, grid, **kwargs):
        grid_radii = self.radial_grid_from(grid=grid, **kwargs)
        return self._cartesian_grid_via_radial_from(
            grid=grid, radius=(self.kappa * grid_radii)
        )
