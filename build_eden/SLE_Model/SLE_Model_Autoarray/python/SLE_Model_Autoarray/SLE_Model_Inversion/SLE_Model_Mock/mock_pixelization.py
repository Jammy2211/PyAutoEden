import numpy as np
from SLE_Model_Autoarray.SLE_Model_Mask.mask_2d import Mask2D
from SLE_Model_Autoarray.SLE_Model_Inversion.SLE_Model_Pixelization.pixelization import (
    Pixelization,
)


class MockPixelization(Pixelization):
    def __init__(
        self,
        mesh=None,
        regularization=None,
        image_mesh=None,
        mapper=None,
        image_plane_mesh_grid=None,
    ):
        super().__init__(
            mesh=mesh, regularization=regularization, image_mesh=image_mesh
        )
        self.mapper = mapper
        self.image_plane_mesh_grid = image_plane_mesh_grid

    def mapper_grids_from(
        self,
        mask,
        source_plane_data_grid,
        source_plane_mesh_grid,
        image_plane_mesh_grid=None,
        adapt_data=None,
        settings=None,
        preloads=None,
        run_time_dict=None,
    ):
        return self.mapper

    def image_plane_mesh_grid_from(self, mask, adapt_data, settings=None):
        if (adapt_data is not None) and (self.image_plane_mesh_grid is not None):
            return adapt_data * self.image_plane_mesh_grid
        return self.image_plane_mesh_grid
