import numpy as np
from typing import Dict, Optional
from SLE_Model_Autoarray.SLE_Model_Inversion.SLE_Model_Pixelization.SLE_Model_Mesh.abstract import (
    AbstractMesh,
)
from SLE_Model_Autoarray.SLE_Model_Inversion.SLE_Model_Pixelization.settings import (
    SettingsPixelization,
)
from SLE_Model_Autoarray.SLE_Model_Inversion.SLE_Model_Pixelization.SLE_Model_Mappers.mapper_grids import (
    MapperGrids,
)
from SLE_Model_Autoarray.SLE_Model_Structures.SLE_Model_Grids.uniform_2d import Grid2D
from SLE_Model_Autoarray.SLE_Model_Structures.SLE_Model_Grids.sparse_2d import (
    Grid2DSparse,
)
from SLE_Model_Autoarray.preloads import Preloads


class MockMesh(AbstractMesh):
    def __init__(self, image_plane_mesh_grid=None):
        super().__init__()
        self.image_plane_mesh_grid = image_plane_mesh_grid

    def mapper_grids_from(
        self,
        source_plane_data_grid,
        source_plane_mesh_grid=None,
        image_plane_mesh_grid=None,
        hyper_data=None,
        settings=SettingsPixelization(),
        preloads=Preloads(),
        profiling_dict=None,
    ):
        return MapperGrids(
            source_plane_data_grid=source_plane_data_grid,
            source_plane_mesh_grid=source_plane_mesh_grid,
            image_plane_mesh_grid=self.image_plane_mesh_grid,
            hyper_data=hyper_data,
            settings=settings,
            preloads=preloads,
            profiling_dict=profiling_dict,
        )

    def image_plane_mesh_grid_from(
        self, image_plane_data_grid, hyper_data, settings=None
    ):
        if (hyper_data is not None) and (self.image_plane_mesh_grid is not None):
            return hyper_data * self.image_plane_mesh_grid
        return self.image_plane_mesh_grid
