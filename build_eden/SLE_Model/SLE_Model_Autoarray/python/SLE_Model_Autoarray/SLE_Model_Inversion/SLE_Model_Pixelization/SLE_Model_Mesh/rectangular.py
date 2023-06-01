import numpy as np
from typing import Dict, Optional, Tuple
from SLE_Model_Autoarray.SLE_Model_Structures.SLE_Model_Grids.uniform_2d import Grid2D
from SLE_Model_Autoarray.SLE_Model_Structures.SLE_Model_Mesh.rectangular_2d import (
    Mesh2DRectangular,
)
from SLE_Model_Autoarray.preloads import Preloads
from SLE_Model_Autoarray.SLE_Model_Inversion.SLE_Model_Pixelization.SLE_Model_Mappers.mapper_grids import (
    MapperGrids,
)
from SLE_Model_Autoarray.SLE_Model_Inversion.SLE_Model_Pixelization.SLE_Model_Mesh.abstract import (
    AbstractMesh,
)
from SLE_Model_Autoarray.SLE_Model_Inversion.SLE_Model_Pixelization.settings import (
    SettingsPixelization,
)
from SLE_Model_Autoarray import exc
from SLE_Model_Autoarray.numba_util import profile_func


class Rectangular(AbstractMesh):
    def __init__(self, shape=(3, 3)):
        """
        A uniform mesh of rectangular pixels, which without interpolation are paired with a 2D grid of (y,x)
        coordinates.

        For a full description of how a mesh is paired with another grid,
        see the :meth:`Pixelization API documentation <autoarray.inversion.pixelization.pixelization.Pixelization>`.

        The rectangular grid is uniform, has dimensions (total_y_pixels, total_x_pixels) and has indexing beginning
        in the top-left corner and going rightwards and downwards.

        A ``Pixelization`` using a ``Rectangular`` mesh has three grids associated with it:

        - ``image_plane_data_grid``: The observed data grid in the image-plane (which is paired with the mesh in
          the source-plane).
        - ``source_plane_data_grid``: The observed data grid mapped to the source-plane after gravitational lensing.
        - ``source_plane_mesh_grid``: The centres of each rectangular pixel.

        It does not have a ``image_plane_mesh_grid`` because a rectangular pixelization is constructed by overlaying
        a grid of rectangular over the `source_plane_data_grid`.

        Each (y,x) coordinate in the `source_plane_data_grid` is associated with the rectangular pixelization pixel
        it falls within. No interpolation is performed when making these associations.
        Parameters
        ----------
        shape
            The 2D dimensions of the rectangular grid of pixels (total_y_pixels, total_x_pixel).
        """
        if (shape[0] <= 2) or (shape[1] <= 2):
            raise exc.MeshException(
                "The rectangular pixelization must be at least dimensions 3x3"
            )
        self.shape = (int(shape[0]), int(shape[1]))
        self.pixels = self.shape[0] * self.shape[1]
        super().__init__()
        self.profiling_dict = {}

    @property
    def uses_interpolation(self):
        """
        Does this ``Mesh`` object use interpolation when pairing with another 2D grid?
        """
        return False

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
        """
        Mapper objects describe the mappings between pixels in the masked 2D data and the pixels in a pixelization,
        in both the `data` and `source` frames.

        This function returns a `MapperRectangularNoInterp` as follows:

        1) If `settings.use_border=True`, the border of the input `source_plane_data_grid` is used to relocate all of the
           grid's (y,x) coordinates beyond the border to the edge of the border.

        2) Determine the (y,x) coordinates of the pixelization's rectangular pixels, by laying this rectangular grid
           over the 2D grid of relocated (y,x) coordinates computed in step 1 (or the input `source_plane_data_grid` if step 1
           is bypassed).

        3) Return the `MapperRectangularNoInterp`.

        Parameters
        ----------
        source_plane_data_grid
            A 2D grid of (y,x) coordinates associated with the unmasked 2D data after it has been transformed to the
            `source` reference frame.
        source_plane_mesh_grid
            Not used for a rectangular pixelization, because the pixelization grid in the `source` frame is computed
            by overlaying the `source_plane_data_grid` with the rectangular pixelization.
        image_plane_mesh_grid
            Not used for a rectangular pixelization.
        hyper_data
            Not used for a rectangular pixelization.
        settings
            Settings controlling the pixelization for example if a border is used to relocate its exterior coordinates.
        preloads
            Object which may contain preloaded arrays of quantities computed in the pixelization, which are passed via
            this object speed up the calculation.
        profiling_dict
            A dictionary which contains timing of certain functions calls which is used for profiling.
        """
        self.profiling_dict = profiling_dict
        relocated_grid = self.relocated_grid_from(
            source_plane_data_grid=source_plane_data_grid,
            settings=settings,
            preloads=preloads,
        )
        mesh_grid = self.mesh_grid_from(source_plane_data_grid=relocated_grid)
        return MapperGrids(
            source_plane_data_grid=relocated_grid,
            source_plane_mesh_grid=mesh_grid,
            image_plane_mesh_grid=image_plane_mesh_grid,
            hyper_data=hyper_data,
            preloads=preloads,
            profiling_dict=profiling_dict,
        )

    @profile_func
    def mesh_grid_from(
        self,
        source_plane_data_grid=None,
        source_plane_mesh_grid=None,
        sparse_index_for_slim_index=None,
    ):
        """
        Return the rectangular `source_plane_mesh_grid` as a `Mesh2DRectangular` object, which provides additional
        functionality for perform operatons that exploit the geometry of a rectangular pixelization.

        Parameters
        ----------
        source_plane_data_grid
            The (y,x) grid of coordinates over which the rectangular pixelization is overlaid, where this grid may have
            had exterior pixels relocated to its edge via the border.
        source_plane_mesh_grid
            Not used for a rectangular pixelization, because the pixelization grid in the `source` frame is computed
            by overlaying the `source_plane_data_grid` with the rectangular pixelization.
        sparse_index_for_slim_index
            Not used for a rectangular pixelization.
        """
        return Mesh2DRectangular.overlay_grid(
            shape_native=self.shape, grid=source_plane_data_grid
        )

    def image_plane_mesh_grid_from(
        self, image_plane_data_grid, hyper_data=None, settings=SettingsPixelization()
    ):
        """
        Not used for rectangular pixelization.
        """
        return None