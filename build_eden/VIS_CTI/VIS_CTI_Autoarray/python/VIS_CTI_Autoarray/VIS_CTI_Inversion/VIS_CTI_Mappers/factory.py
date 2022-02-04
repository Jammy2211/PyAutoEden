from VIS_CTI_Autoarray.VIS_CTI_Structures.VIS_CTI_Grids.VIS_CTI_TwoD.grid_2d_pixelization import (
    Grid2DRectangular,
)
from VIS_CTI_Autoarray.VIS_CTI_Structures.VIS_CTI_Grids.VIS_CTI_TwoD.grid_2d_pixelization import (
    Grid2DDelaunay,
)
from VIS_CTI_Autoarray.VIS_CTI_Structures.VIS_CTI_Grids.VIS_CTI_TwoD.grid_2d_pixelization import (
    Grid2DVoronoi,
)


def mapper_from(
    source_grid_slim,
    source_pixelization_grid,
    data_pixelization_grid=None,
    hyper_data=None,
):
    from VIS_CTI_Autoarray.VIS_CTI_Inversion.VIS_CTI_Mappers.rectangular import (
        MapperRectangularNoInterp,
    )
    from VIS_CTI_Autoarray.VIS_CTI_Inversion.VIS_CTI_Mappers.delaunay import (
        MapperDelaunay,
    )
    from VIS_CTI_Autoarray.VIS_CTI_Inversion.VIS_CTI_Mappers.voronoi import (
        MapperVoronoi,
    )
    from VIS_CTI_Autoarray.VIS_CTI_Inversion.VIS_CTI_Mappers.voronoi import (
        MapperVoronoiNoInterp,
    )

    if isinstance(source_pixelization_grid, Grid2DRectangular):
        return MapperRectangularNoInterp(
            source_grid_slim=source_grid_slim,
            source_pixelization_grid=source_pixelization_grid,
            data_pixelization_grid=data_pixelization_grid,
            hyper_image=hyper_data,
        )
    elif isinstance(source_pixelization_grid, Grid2DDelaunay):
        return MapperDelaunay(
            source_grid_slim=source_grid_slim,
            source_pixelization_grid=source_pixelization_grid,
            data_pixelization_grid=data_pixelization_grid,
            hyper_image=hyper_data,
        )
    elif isinstance(source_pixelization_grid, Grid2DVoronoi):
        if source_pixelization_grid.uses_interpolation:
            return MapperVoronoi(
                source_grid_slim=source_grid_slim,
                source_pixelization_grid=source_pixelization_grid,
                data_pixelization_grid=data_pixelization_grid,
                hyper_image=hyper_data,
            )
        else:
            return MapperVoronoiNoInterp(
                source_grid_slim=source_grid_slim,
                source_pixelization_grid=source_pixelization_grid,
                data_pixelization_grid=data_pixelization_grid,
                hyper_image=hyper_data,
            )
