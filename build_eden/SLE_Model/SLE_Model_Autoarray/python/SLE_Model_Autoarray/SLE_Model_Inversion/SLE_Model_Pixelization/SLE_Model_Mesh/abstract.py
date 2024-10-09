import numpy as np
from typing import Dict, Optional
from SLE_Model_Autoarray.SLE_Model_Inversion.SLE_Model_Pixelization.SLE_Model_Mappers.mapper_grids import (
    MapperGrids,
)
from SLE_Model_Autoarray.SLE_Model_Inversion.SLE_Model_Pixelization.border_relocator import (
    BorderRelocator,
)
from SLE_Model_Autoarray.SLE_Model_Structures.SLE_Model_Grids.uniform_2d import Grid2D
from SLE_Model_Autoarray.SLE_Model_Structures.SLE_Model_Grids.irregular_2d import (
    Grid2DIrregular,
)
from SLE_Model_Autoarray.preloads import Preloads
from SLE_Model_Autoarray.numba_util import profile_func


class AbstractMesh:
    def __eq__(self, other):
        return (self.__dict__ == other.__dict__) and (self.__class__ is other.__class__)

    @profile_func
    def relocated_grid_from(
        self, border_relocator, source_plane_data_grid, preloads=Preloads()
    ):
        """
        Relocates all coordinates of the input `source_plane_data_grid` that are outside of a
        border (which is defined by a grid of (y,x) coordinates) to the edge of this border.

        The border is determined from the mask of the 2D data in the `data` frame before any transformations of the
        data's grid are performed. The border is all pixels in this mask that are pixels at its extreme edge. These
        pixel indexes are used to then determine a grid of (y,x) coordinates from the transformed `source_grid_grid` in
        the `source` reference frame, whereby points located outside of it are relocated to the border's edge.

        A full description of relocation is given in the method grid_2d.relocated_grid_from()`.

        This is used in the project PyAutoLens to relocate the coordinates that are ray-traced near the centre of mass
        of galaxies, which are heavily demagnified and may trace to outskirts of the source-plane well beyond the
        border.

        Parameters
        ----------
        border_relocator
           The border relocator, which relocates coordinates outside the border of the source-plane data grid to its
           edge.
        source_plane_data_grid
            A 2D (y,x) grid of coordinates, whose coordinates outside the border are relocated to its edge.
        preloads
            Contains quantities which may already be computed and can be preloaded to speed up calculations, in this
            case the relocated grid.
        """
        if preloads.relocated_grid is None:
            if border_relocator is not None:
                return border_relocator.relocated_grid_from(grid=source_plane_data_grid)
            return source_plane_data_grid
        return preloads.relocated_grid

    @profile_func
    def relocated_mesh_grid_from(
        self, border_relocator, source_plane_data_grid, source_plane_mesh_grid
    ):
        """
        Relocates all coordinates of the input `source_plane_mesh_grid` that are outside of a border (which
        is defined by a grid of (y,x) coordinates) to the edge of this border.

        The border is determined from the mask of the 2D data in the `data` frame before any transformations of the
        data's grid are performed. The border is all pixels in this mask that are pixels at its extreme edge. These
        pixel indexes are used to then determine a grid of (y,x) coordinates from the transformed `source_grid_grid` in
        the `source` reference frame, whereby points located outside of it are relocated to the border's edge.

        A full description of relocation is given in the method grid_2d.relocated_grid_from()`.

        This is used in the project `PyAutoLens` to relocate the coordinates that are ray-traced near the centre of mass
        of galaxies, which are heavily demagnified and may trace to outskirts of the source-plane well beyond the
        border.

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
        """
        if border_relocator is not None:
            return border_relocator.relocated_mesh_grid_from(
                grid=source_plane_data_grid, mesh_grid=source_plane_mesh_grid
            )
        return source_plane_mesh_grid

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
        raise NotImplementedError

    def mesh_grid_from(self, source_plane_data_grid, source_plane_mesh_grid):
        raise NotImplementedError

    @property
    def requires_image_mesh(self):
        return True

    def __str__(self):
        return """
""".join(
            ["{}: {}".format(k, v) for (k, v) in self.__dict__.items()]
        )

    def __repr__(self):
        return """{}
{}""".format(
            self.__class__.__name__, str(self)
        )
