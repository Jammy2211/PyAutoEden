import numpy as np
from typing import Dict, Optional
from SLE_Model_Autoarray.SLE_Model_Structures.SLE_Model_Grids.uniform_2d import Grid2D
from SLE_Model_Autoarray.SLE_Model_Structures.SLE_Model_Grids.irregular_2d import (
    Grid2DIrregular,
)
from SLE_Model_Autoarray.preloads import Preloads
from SLE_Model_Autoarray.SLE_Model_Inversion.SLE_Model_Pixelization.SLE_Model_Mappers.mapper_grids import (
    MapperGrids,
)
from SLE_Model_Autoarray.SLE_Model_Inversion.SLE_Model_Pixelization.SLE_Model_Mesh.abstract import (
    AbstractMesh,
)
from SLE_Model_Autoarray.SLE_Model_Inversion.SLE_Model_Pixelization.border_relocator import (
    BorderRelocator,
)


class Triangulation(AbstractMesh):
    def mapper_grids_from(
        self,
        mask,
        source_plane_data_grid,
        border_relocator=None,
        source_plane_mesh_grid=None,
        image_plane_mesh_grid=None,
        adapt_data=None,
        preloads=Preloads(),
        run_time_dict=None,
    ):
        """
        Mapper objects describe the mappings between pixels in the masked 2D data and the pixels in a mesh,
        in both the `data` and `source` frames.

        This function returns a `MapperVoronoi` as follows:

        1) Before this routine is called, a sparse grid of (y,x) coordinates are computed from the 2D masked data,
           the `image_plane_mesh_grid`, which acts as the Voronoi pixel centres of the mesh and mapper.

        2) Before this routine is called, operations are performed on this `image_plane_mesh_grid` that transform it
           from a 2D grid which overlaps with the 2D mask of the data in the `data` frame to an irregular grid in
           the `source` frame, the `source_plane_mesh_grid`.

        3) If the border relocator is input, the border of the input `source_plane_data_grid` is used to relocate all of the
           grid's (y,x) coordinates beyond the border to the edge of the border.

        4) If the border relocatiro is input, the border of the input `source_plane_data_grid` is used to relocate all of the
           transformed `source_plane_mesh_grid`'s (y,x) coordinates beyond the border to the edge of the border.

        5) Use the transformed `source_plane_mesh_grid`'s (y,x) coordinates as the centres of the Voronoi mesh.

        6) Return the `MapperVoronoi`.

        Parameters
        ----------
        border_relocator
           The border relocator, which relocates coordinates outside the border of the source-plane data grid to its
           edge.
        source_plane_data_grid
            A 2D grid of (y,x) coordinates associated with the unmasked 2D data after it has been transformed to the
            `source` reference frame.
        source_plane_mesh_grid
            The centres of every Voronoi pixel in the `source` frame, which are initially derived by computing a sparse
            set of (y,x) coordinates computed from the unmasked data in the `data` frame and applying a transformation
            to this.
        image_plane_mesh_grid
            The sparse set of (y,x) coordinates computed from the unmasked data in the `data` frame. This has a
            transformation applied to it to create the `source_plane_mesh_grid`.
        adapt_data
            Not used for a rectangular mesh.
        preloads
            Object which may contain preloaded arrays of quantities computed in the mesh, which are passed via
            this object speed up the calculation.
        run_time_dict
            A dictionary which contains timing of certain functions calls which is used for profiling.
        """
        self.run_time_dict = run_time_dict
        source_plane_data_grid = self.relocated_grid_from(
            border_relocator=border_relocator,
            source_plane_data_grid=source_plane_data_grid,
            preloads=preloads,
        )
        relocated_source_plane_mesh_grid = self.relocated_mesh_grid_from(
            border_relocator=border_relocator,
            source_plane_data_grid=source_plane_data_grid,
            source_plane_mesh_grid=source_plane_mesh_grid,
        )
        try:
            source_plane_mesh_grid = self.mesh_grid_from(
                source_plane_data_grid=source_plane_data_grid,
                source_plane_mesh_grid=relocated_source_plane_mesh_grid,
            )
        except ValueError as e:
            raise e
        return MapperGrids(
            mask=mask,
            source_plane_data_grid=source_plane_data_grid,
            source_plane_mesh_grid=source_plane_mesh_grid,
            image_plane_mesh_grid=image_plane_mesh_grid,
            adapt_data=adapt_data,
            preloads=preloads,
            run_time_dict=run_time_dict,
        )
