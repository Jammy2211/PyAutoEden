import numpy as np
from SLE_Model_Autoarray.SLE_Model_Inversion.SLE_Model_LinearObj.func_list import (
    AbstractLinearObjFuncList,
)


class MockLinearObjFuncList(AbstractLinearObjFuncList):
    def __init__(
        self,
        parameters=None,
        grid=None,
        mapping_matrix=None,
        regularization=None,
        operated_mapping_matrix_override=None,
    ):
        super().__init__(grid=grid, regularization=regularization)
        self._parameters = parameters
        self._mapping_matrix = mapping_matrix
        self._operated_mapping_matrix_override = operated_mapping_matrix_override

    @property
    def params(self):
        return self._parameters

    @property
    def mapping_matrix(self):
        return self._mapping_matrix

    @property
    def operated_mapping_matrix_override(self):
        return self._operated_mapping_matrix_override
