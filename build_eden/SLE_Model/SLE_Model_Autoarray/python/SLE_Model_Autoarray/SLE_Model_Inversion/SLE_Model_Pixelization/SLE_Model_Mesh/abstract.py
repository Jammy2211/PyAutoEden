import numpy as np
from typing import Dict, Optional
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
from SLE_Model_Autoarray.numba_util import profile_func


class AbstractMesh:
    def __eq__(self, other):
        return (self.__dict__ == other.__dict__) and (self.__class__ is other.__class__)

    @profile_func
    def relocated_grid_from(
        self,
        source_plane_data_grid,
        settings=SettingsPixelization(),
        preloads=Preloads(),
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
        source_plane_data_grid
            A 2D (y,x) grid of coordinates, whose coordinates outside the border are relocated to its edge.
        """
        if preloads.relocated_grid is None:
            if settings.use_border:
                return source_plane_data_grid.relocated_grid_from(
                    grid=source_plane_data_grid
                )
            return source_plane_data_grid
        return preloads.relocated_grid

    @profile_func
    def relocated_mesh_grid_from(
        self,
        source_plane_data_grid,
        source_plane_mesh_grid,
        settings=SettingsPixelization(),
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
        source_plane_data_grid
            A 2D grid of (y,x) coordinates associated with the unmasked 2D data after it has been transformed to the
            `source` reference frame.
        source_plane_mesh_grid
            The centres of every Voronoi pixel in the `source` frame, which are initially derived by computing a sparse
            set of (y,x) coordinates computed from the unmasked data in the `data` frame and applying a transformation
            to this.
        settings
            Settings controlling the pixelization for example if a border is used to relocate its exterior coordinates.
        """
        if settings.use_border:
            return source_plane_data_grid.relocated_mesh_grid_from(
                mesh_grid=source_plane_mesh_grid
            )
        return source_plane_mesh_grid

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
        raise NotImplementedError

    def mesh_grid_from(
        self,
        source_plane_data_grid,
        source_plane_mesh_grid,
        sparse_index_for_slim_index=None,
    ):
        raise NotImplementedError

    def weight_map_from(self, hyper_data):
        raise NotImplementedError()

    @property
    def is_stochastic(self):
        return False

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
