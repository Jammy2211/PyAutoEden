from matplotlib import patches as ptch
from typing import List, Optional, Union
from SLE_Model_Autoarray.SLE_Model_Mask.mask_2d import Mask2D
from SLE_Model_Autoarray.SLE_Model_Plot.SLE_Model_Visuals.abstract import (
    AbstractVisuals,
)
from SLE_Model_Autoarray.SLE_Model_Structures.SLE_Model_Arrays.uniform_1d import Array1D
from SLE_Model_Autoarray.SLE_Model_Structures.SLE_Model_Arrays.uniform_2d import Array2D
from SLE_Model_Autoarray.SLE_Model_Structures.SLE_Model_Grids.uniform_2d import Grid2D
from SLE_Model_Autoarray.SLE_Model_Structures.SLE_Model_Grids.irregular_2d import (
    Grid2DIrregular,
)
from SLE_Model_Autoarray.SLE_Model_Structures.SLE_Model_Vectors.irregular import (
    VectorYX2DIrregular,
)


class Visuals2D(AbstractVisuals):
    def __init__(
        self,
        origin=None,
        mask=None,
        border=None,
        lines=None,
        positions=None,
        grid=None,
        mesh_grid=None,
        vectors=None,
        patches=None,
        array_overlay=None,
        parallel_overscan=None,
        serial_prescan=None,
        serial_overscan=None,
        indexes=None,
        pix_indexes=None,
    ):
        self.origin = origin
        self.mask = mask
        self.border = border
        self.lines = lines
        self.positions = positions
        self.grid = grid
        self.mesh_grid = mesh_grid
        self.vectors = vectors
        self.patches = patches
        self.array_overlay = array_overlay
        self.parallel_overscan = parallel_overscan
        self.serial_prescan = serial_prescan
        self.serial_overscan = serial_overscan
        self.indexes = indexes
        self.pix_indexes = pix_indexes

    def plot_via_plotter(self, plotter, grid_indexes=None, mapper=None):
        if self.origin is not None:
            plotter.origin_scatter.scatter_grid(
                grid=Grid2DIrregular(values=self.origin)
            )
        if self.mask is not None:
            plotter.mask_scatter.scatter_grid(
                grid=self.mask.derive_grid.edge_sub_1.binned
            )
        if self.border is not None:
            plotter.border_scatter.scatter_grid(grid=self.border)
        if self.grid is not None:
            plotter.grid_scatter.scatter_grid(grid=self.grid)
        if self.mesh_grid is not None:
            plotter.mesh_grid_scatter.scatter_grid(grid=self.mesh_grid)
        if self.positions is not None:
            plotter.positions_scatter.scatter_grid(grid=self.positions)
        if self.vectors is not None:
            plotter.vector_yx_quiver.quiver_vectors(vectors=self.vectors)
        if self.patches is not None:
            plotter.patch_overlay.overlay_patches(patches=self.patches)
        if self.lines is not None:
            plotter.grid_plot.plot_grid(grid=self.lines)
        if self.indexes is not None:
            plotter.index_scatter.scatter_grid_indexes(
                grid=grid_indexes, indexes=self.indexes
            )
        if (self.pix_indexes is not None) and (mapper is not None):
            indexes = mapper.pix_indexes_for_slim_indexes(pix_indexes=self.pix_indexes)
            plotter.index_scatter.scatter_grid_indexes(
                grid=mapper.source_plane_data_grid, indexes=indexes
            )