import numpy as np
from typing import List, Tuple, Union

PixelScales = Union[(Tuple[(float, float)], float)]
from VIS_CTI_Autoarray.VIS_CTI_Structures.VIS_CTI_Grids.VIS_CTI_TwoD.grid_2d import (
    Grid2D,
)
from VIS_CTI_Autoarray.VIS_CTI_Structures.VIS_CTI_Grids.VIS_CTI_TwoD.grid_2d_iterate import (
    Grid2DIterate,
)
from VIS_CTI_Autoarray.VIS_CTI_Structures.VIS_CTI_Grids.VIS_CTI_TwoD.grid_2d_irregular import (
    Grid2DIrregular,
)

Grid1D2DLike = Union[(np.ndarray, "Grid1D", Grid2D, Grid2DIterate, Grid2DIrregular)]
Grid2DLike = Union[(np.ndarray, Grid2D, Grid2DIterate, Grid2DIrregular)]
from VIS_CTI_Autoarray.VIS_CTI_Operators.transformer import TransformerDFT
from VIS_CTI_Autoarray.VIS_CTI_Operators.transformer import TransformerNUFFT

Transformer = Union[(TransformerDFT, TransformerNUFFT)]
from VIS_CTI_Autoarray.VIS_CTI_Layout.region import Region1D
from VIS_CTI_Autoarray.VIS_CTI_Layout.region import Region2D

Region1DLike = Union[(Region1D, Tuple[(int, int)])]
Region1DList = Union[(List[Region1D], List[Tuple[(int, int)]])]
Region2DLike = Union[(Region2D, Tuple[(int, int, int, int)])]
Region2DList = Union[(List[Region2D], List[Tuple[(int, int, int, int)]])]
