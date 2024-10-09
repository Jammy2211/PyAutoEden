from SLE_Model_Autofit.jax_wrapper import register_pytree_node_class, numpy as np
from SLE_Model_Autofit.mock import *
from SLE_Model_Autoarray.mock import *
from SLE_Model_Autogalaxy.mock import *
import SLE_Model_Autoarray as aa
from SLE_Model_Autolens import Tracer
from SLE_Model_Autolens.SLE_Model_Imaging.SLE_Model_Mock.mock_fit_imaging import (
    MockFitImaging,
)
from SLE_Model_Autolens.SLE_Model_Lens.SLE_Model_Mock.mock_tracer import MockTracer
from SLE_Model_Autolens.SLE_Model_Lens.SLE_Model_Mock.mock_tracer import MockTracerPoint
from SLE_Model_Autolens.SLE_Model_Point.SLE_Model_Mock.mock_solver import (
    MockPointSolver,
)


@register_pytree_node_class
class NullTracer(Tracer):
    def __init__(self):
        super().__init__([])

    def deflections_yx_2d_from(self, grid):
        return np.zeros_like(grid.array)

    def deflections_between_planes_from(self, grid, plane_i=0, plane_j=(-1)):
        return np.zeros_like(grid.array)

    def magnification_2d_via_hessian_from(
        self, grid, buffer=0.01, deflections_func=None
    ):
        return aa.ArrayIrregular(values=np.ones(grid.shape[0]))

    def tree_flatten(self):
        """
        Flatten this model as a PyTree.
        """
        return ((), None)

    @classmethod
    def tree_unflatten(cls, aux_data, children):
        """
        Unflatten a PyTree into a model.
        """
        return cls()
