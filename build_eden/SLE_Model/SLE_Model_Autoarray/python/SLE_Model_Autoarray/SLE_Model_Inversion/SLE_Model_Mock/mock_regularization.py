from SLE_Model_Autoarray.SLE_Model_Inversion.SLE_Model_Regularization.abstract import (
    AbstractRegularization,
)


class MockRegularization(AbstractRegularization):
    def __init__(self, regularization_matrix=None):
        super().__init__()
        self.regularization_matrix = regularization_matrix

    def regularization_matrix_via_neighbors_from(self, neighbors, neighbors_sizes):
        return self.regularization_matrix

    def regularization_matrix_from(self, linear_obj):
        return self.regularization_matrix
