from typing import Dict, Optional
from SLE_Model_Autoarray.SLE_Model_Inversion.SLE_Model_Pixelization.SLE_Model_Mappers.mapper_grids import (
    MapperGrids,
)
from SLE_Model_Autoarray.SLE_Model_Inversion.SLE_Model_Regularization.abstract import (
    AbstractRegularization,
)
from SLE_Model_Autoarray.SLE_Model_Structures.SLE_Model_Mesh.rectangular_2d import (
    Mesh2DRectangular,
)
from SLE_Model_Autoarray.SLE_Model_Structures.SLE_Model_Mesh.delaunay_2d import (
    Mesh2DDelaunay,
)
from SLE_Model_Autoarray.SLE_Model_Structures.SLE_Model_Mesh.voronoi_2d import (
    Mesh2DVoronoi,
)


def mapper_from(mapper_grids, regularization, profiling_dict=None):
    """
    Factory which given input `MapperGrids` and `Regularization` objects creates a `Mapper`.

    A `Mapper` determines the mappings between a masked dataset's pixels and pixels of a linear object pixelization.
    The mapper is used in order to fit a dataset via an inversion. Docstrings in the packages `linear_obj`, `mesh`,
    `pixelization`, `mapper_grids` `mapper` and `inversion` provide more details.

    This factory inspects the type of mesh contained in the `MapperGrids` and uses this to determine the type of
    `Mapper` it creates. For example, if a Delaunay mesh is used, a `MapperDelaunay` is created.

    Parameters
    ----------
    mapper_grids
        An object containing the data grid and mesh grid in both the data-frame and source-frame used by the
        mapper to map data-points to linear object parameters.
    regularization
        The regularization scheme which may be applied to this linear object in order to smooth its solution,
        which for a mapper smooths neighboring pixels on the mesh.
    profiling_dict
        A dictionary which contains timing of certain functions calls which is used for profiling.

    Returns
    -------
    A mapper whose type is determined by the input `mapper_grids` mesh type.
    """
    from SLE_Model_Autoarray.SLE_Model_Inversion.SLE_Model_Pixelization.SLE_Model_Mappers.rectangular import (
        MapperRectangularNoInterp,
    )
    from SLE_Model_Autoarray.SLE_Model_Inversion.SLE_Model_Pixelization.SLE_Model_Mappers.delaunay import (
        MapperDelaunay,
    )
    from SLE_Model_Autoarray.SLE_Model_Inversion.SLE_Model_Pixelization.SLE_Model_Mappers.voronoi import (
        MapperVoronoi,
    )
    from SLE_Model_Autoarray.SLE_Model_Inversion.SLE_Model_Pixelization.SLE_Model_Mappers.voronoi import (
        MapperVoronoiNoInterp,
    )

    if isinstance(mapper_grids.source_plane_mesh_grid, Mesh2DRectangular):
        return MapperRectangularNoInterp(
            mapper_grids=mapper_grids,
            regularization=regularization,
            profiling_dict=profiling_dict,
        )
    elif isinstance(mapper_grids.source_plane_mesh_grid, Mesh2DDelaunay):
        return MapperDelaunay(
            mapper_grids=mapper_grids,
            regularization=regularization,
            profiling_dict=profiling_dict,
        )
    elif isinstance(mapper_grids.source_plane_mesh_grid, Mesh2DVoronoi):
        if mapper_grids.source_plane_mesh_grid.uses_interpolation:
            return MapperVoronoi(
                mapper_grids=mapper_grids,
                regularization=regularization,
                profiling_dict=profiling_dict,
            )
        return MapperVoronoiNoInterp(
            mapper_grids=mapper_grids,
            regularization=regularization,
            profiling_dict=profiling_dict,
        )
