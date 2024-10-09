from typing import Dict, Optional
from SLE_Model_Autoarray.SLE_Model_Inversion.SLE_Model_Pixelization.SLE_Model_Mappers.mapper_grids import (
    MapperGrids,
)
from SLE_Model_Autoarray.SLE_Model_Inversion.SLE_Model_Pixelization.border_relocator import (
    BorderRelocator,
)
from SLE_Model_Autoarray.SLE_Model_Operators.SLE_Model_OverSampling.abstract import (
    AbstractOverSampler,
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


def mapper_from(
    mapper_grids,
    regularization,
    over_sampler,
    border_relocator=None,
    run_time_dict=None,
):
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
    run_time_dict
        A dictionary which contains timing of certain functions calls which is used for profiling.

    Returns
    -------
    A mapper whose type is determined by the input `mapper_grids` mesh type.
    """
    from SLE_Model_Autoarray.SLE_Model_Inversion.SLE_Model_Pixelization.SLE_Model_Mappers.rectangular import (
        MapperRectangular,
    )
    from SLE_Model_Autoarray.SLE_Model_Inversion.SLE_Model_Pixelization.SLE_Model_Mappers.delaunay import (
        MapperDelaunay,
    )
    from SLE_Model_Autoarray.SLE_Model_Inversion.SLE_Model_Pixelization.SLE_Model_Mappers.voronoi import (
        MapperVoronoi,
    )

    if isinstance(mapper_grids.source_plane_mesh_grid, Mesh2DRectangular):
        return MapperRectangular(
            mapper_grids=mapper_grids,
            over_sampler=over_sampler,
            border_relocator=border_relocator,
            regularization=regularization,
            run_time_dict=run_time_dict,
        )
    elif isinstance(mapper_grids.source_plane_mesh_grid, Mesh2DDelaunay):
        return MapperDelaunay(
            mapper_grids=mapper_grids,
            over_sampler=over_sampler,
            border_relocator=border_relocator,
            regularization=regularization,
            run_time_dict=run_time_dict,
        )
    elif isinstance(mapper_grids.source_plane_mesh_grid, Mesh2DVoronoi):
        return MapperVoronoi(
            mapper_grids=mapper_grids,
            over_sampler=over_sampler,
            border_relocator=border_relocator,
            regularization=regularization,
            run_time_dict=run_time_dict,
        )
