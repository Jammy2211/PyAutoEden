import logging
import numpy as np
from typing import List, Tuple, Union
from VIS_CTI_Autoarray.VIS_CTI_Structures.VIS_CTI_Vectors.abstract import (
    AbstractVectorYX2D,
)
from VIS_CTI_Autoarray.VIS_CTI_Structures.VIS_CTI_Grids.VIS_CTI_TwoD.grid_2d_irregular import (
    Grid2DIrregular,
)
from VIS_CTI_Autoarray.VIS_CTI_Structures.VIS_CTI_Arrays.values import ValuesIrregular
from VIS_CTI_Autoarray import exc

logging.basicConfig()
logger = logging.getLogger(__name__)


class VectorYX2DIrregular(AbstractVectorYX2D):
    def __new__(cls, vectors, grid):
        """
        A collection of (y,x) vectors which are located on a irregular 2D grid of (y,x) coordinates.

        The (y,x) vectors are stored as a 2D NumPy array of shape [total_vectors, 2]. This array can be mapped to a
        list of tuples structure.

        Calculations should use the NumPy array structure wherever possible for efficient calculations.

        The vectors input to this function can have any of the following forms (they will be converted to the 1D NumPy
        array structure and can be converted back using the object's properties):

        [[vector_0_y, vector_0_x], [vector_1_y, vector_1_x]]
        [(vector_0_y, vector_0_x), (vector_1_y, vector_1_x)]

        If your vector field lies on a 2D uniform grid of data the `VectorField` data structure should be used.

        Parameters
        ----------
        vectors
            The 2D (y,x) vectors on an irregular grid that represent the vector-field.
        grid
            The irregular grid of (y,x) coordinates where each vector is located.
        """
        if len(vectors) == 0:
            return []
        if type(vectors) is list:
            vectors = np.asarray(vectors)
        obj = vectors.view(cls)
        obj.grid = Grid2DIrregular(grid=grid)
        return obj

    def __array_finalize__(self, obj):
        if hasattr(obj, "grid"):
            self.grid = obj.grid

    @property
    def slim(self):
        """
        The vector-field in its 1D representation, an ndarray of shape [total_vectors, 2].
        """
        return self

    @property
    def in_list(self):
        """
        The vector-field in its list representation, as list of (y,x) vector tuples in a structure
        [(vector_0_y, vector_0_x), ...].
        """
        return [tuple(vector) for vector in self.slim]

    @property
    def magnitudes(self):
        """
        Returns the magnitude of every vector which are computed as sqrt(y**2 + x**2).
        """
        return ValuesIrregular(
            values=np.sqrt(((self[:, 0] ** 2.0) + (self[:, 1] ** 2.0)))
        )

    @property
    def average_magnitude(self):
        """
        The average magnitude of the vector field, where averaging is performed on the (vector_y, vector_x) components.
        """
        return np.sqrt(((np.mean(self[:, 0]) ** 2) + (np.mean(self[:, 1]) ** 2)))

    @property
    def average_phi(self):
        """
        The average angle of the vector field, where averaging is performed on the (vector_y, vector_x) components.
        """
        return (0.5 * np.arctan2(np.mean(self[:, 0]), np.mean(self[:, 1]))) * (
            180 / np.pi
        )

    def vectors_within_radius(self, radius, centre=(0.0, 0.0)):
        """
        Returns a new `VectorYX2DIrregular` object which has had all vectors outside of a circle of input radius
        around an  input (y,x) centre removed.

        Parameters
        ----------
        radius
            The radius of the circle outside of which vectors are removed.
        centre
            The centre of the circle outside of which vectors are removed.

        Returns
        -------
        VectorYX2DIrregular
            The vector field where all vectors outside of the input radius are removed.

        """
        squared_distances = self.grid.distances_to_coordinate(coordinate=centre)
        mask = squared_distances < radius
        if np.all((mask == False)):
            raise exc.VectorFieldException(
                "The input radius removed all vectors / points on the grid."
            )
        return VectorYX2DIrregular(
            vectors=self[mask], grid=Grid2DIrregular(self.grid[mask])
        )

    def vectors_within_annulus(self, inner_radius, outer_radius, centre=(0.0, 0.0)):
        """
        Returns a new `VectorFieldIrregular` object which has had all vectors outside of a circle of input radius
        around an  input (y,x) centre removed.

        Parameters
        ----------
        radius
            The radius of the circle outside of which vectors are removed.
        centre
            The centre of the circle outside of which vectors are removed.

        Returns
        -------
        VectorFieldIrregular
            The vector field where all vectors outside of the input radius are removed.

        """
        squared_distances = self.grid.distances_to_coordinate(coordinate=centre)
        mask = (inner_radius < squared_distances) & (squared_distances < outer_radius)
        if np.all((mask == False)):
            raise exc.VectorFieldException(
                "The input radius removed all vectors / points on the grid."
            )
        return VectorYX2DIrregular(
            vectors=self[mask], grid=Grid2DIrregular(self.grid[mask])
        )
