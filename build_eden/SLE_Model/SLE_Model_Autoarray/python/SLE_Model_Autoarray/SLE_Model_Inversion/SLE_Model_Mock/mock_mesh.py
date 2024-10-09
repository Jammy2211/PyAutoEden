import numpy as np
from typing import Dict, Optional
from SLE_Model_Autoarray.SLE_Model_Mask.mask_2d import Mask2D
from SLE_Model_Autoarray.SLE_Model_Inversion.SLE_Model_Pixelization.SLE_Model_Mesh.abstract import (
    AbstractMesh,
)
from SLE_Model_Autoarray.SLE_Model_Structures.SLE_Model_Mesh.abstract_2d import (
    Abstract2DMesh,
)
from SLE_Model_Autoarray.SLE_Model_Inversion.SLE_Model_Pixelization.SLE_Model_Mappers.mapper_grids import (
    MapperGrids,
)
from SLE_Model_Autoarray.SLE_Model_Structures.SLE_Model_Grids.uniform_2d import Grid2D
from SLE_Model_Autoarray.SLE_Model_Structures.SLE_Model_Grids.irregular_2d import (
    Grid2DIrregular,
)
from SLE_Model_Autoarray.preloads import Preloads


class MockMesh(AbstractMesh):
    def __init__(self, image_plane_mesh_grid=None):
        super().__init__()
        self.image_plane_mesh_grid = image_plane_mesh_grid

    def mapper_grids_from(
        self,
        mask=None,
        source_plane_data_grid=None,
        border_relocator=None,
        source_plane_mesh_grid=None,
        image_plane_mesh_grid=None,
        adapt_data=None,
        preloads=None,
        run_time_dict=None,
    ):
        return MapperGrids(
            mask=mask,
            source_plane_data_grid=source_plane_data_grid,
            border_relocator=border_relocator,
            source_plane_mesh_grid=source_plane_mesh_grid,
            image_plane_mesh_grid=self.image_plane_mesh_grid,
            adapt_data=adapt_data,
            preloads=preloads,
            run_time_dict=run_time_dict,
        )

    def image_plane_mesh_grid_from(self, mask, adapt_data, settings=None):
        if (adapt_data is not None) and (self.image_plane_mesh_grid is not None):
            return adapt_data * self.image_plane_mesh_grid
        return self.image_plane_mesh_grid

    @property
    def requires_image_mesh(self):
        return False
