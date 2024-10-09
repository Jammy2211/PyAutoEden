import numpy as np
from typing import Tuple, List
from SLE_Model_Autoarray.SLE_Model_Geometry.abstract_2d import AbstractGeometry2D
from SLE_Model_Autoarray.SLE_Model_Inversion.SLE_Model_LinearObj.neighbors import (
    Neighbors,
)
from SLE_Model_Autoarray.SLE_Model_Structures.abstract_structure import Structure
from SLE_Model_Autoarray.SLE_Model_Structures.SLE_Model_Mesh.abstract_2d import (
    Abstract2DMesh,
)


class MockGeometry(AbstractGeometry2D):
    def __init__(self, extent):
        self._extent = extent

    @property
    def extent(self):
        return self._extent


class MockGrid2DMesh(Abstract2DMesh):
    @property
    def pixels(self):
        raise NotImplementedError()

    @property
    def slim(self):
        raise NotImplementedError()

    @property
    def native(self):
        raise NotImplementedError()

    def __init__(self, grid=None, extent=None):
        """
        A grid of (y,x) coordinates which represent a uniform rectangular pixelization.

        A `Mesh2DRectangular` is ordered such pixels begin from the top-row and go rightwards and then downwards.
        It is an ndarray of shape [total_pixels, 2], where the first dimension of the ndarray corresponds to the
        pixelization's pixel index and second element whether it is a y or x arc-second coordinate.

        For example:

        - grid[3,0] = the y-coordinate of the 4th pixel in the rectangular pixelization.
        - grid[6,1] = the x-coordinate of the 7th pixel in the rectangular pixelization.

        This class is used in conjuction with the `inversion/pixelizations` package to create rectangular pixelizations
        and mappers that perform an `Inversion`.

        Parameters
        ----------
        grid
            The grid of (y,x) coordinates corresponding to the centres of each pixel in the rectangular pixelization.
        shape_native
            The 2D dimensions of the rectangular pixelization with shape (y_pixels, x_pixel).
        pixel_scales
            The (y,x) scaled units to pixel units conversion factors of every pixel. If this is input as a `float`,
            it is converted to a (float, float) structure.
        origin
            The (y,x) origin of the pixelization.
        """
        if grid is None:
            grid = np.ones(shape=(1, 2))
        self._extent = extent
        super().__init__(grid)

    @property
    def geometry(self):
        return MockGeometry(extent=self.extent)

    @property
    def extent(self):
        return self._extent


class MockMeshGrid:
    def __init__(self, neighbors=None, neighbors_sizes=None):
        self.neighbors = Neighbors(arr=neighbors, sizes=neighbors_sizes)
        self.shape = (len(self.neighbors.sizes),)
