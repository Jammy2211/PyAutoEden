import numpy as np
from VIS_CTI_Autoarray.VIS_CTI_Structures.VIS_CTI_Grids.VIS_CTI_TwoD.grid_2d import (
    Grid2D,
)


class Grid2DTransformed(Grid2D):
    pass


class Grid2DTransformedNumpy(np.ndarray):
    def __new__(cls, grid, *args, **kwargs):
        return grid.view(cls)
