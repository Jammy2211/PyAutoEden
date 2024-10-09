import numpy as np
from typing import List, Tuple, Union

PixelScales = Union[(Tuple[float], Tuple[(float, float)], float)]
from SLE_Model_Autoarray.SLE_Model_Mask.mask_1d import Mask1D
from SLE_Model_Autoarray.SLE_Model_Mask.mask_2d import Mask2D

Mask1D2DLike = Union[(Mask1D, Mask2D)]
from SLE_Model_Autoarray.SLE_Model_Structures.SLE_Model_Arrays.uniform_1d import Array1D
from SLE_Model_Autoarray.SLE_Model_Structures.SLE_Model_Arrays.uniform_2d import Array2D

Array1D2DLike = Union[(Array1D, Array2D)]
from SLE_Model_Autoarray.SLE_Model_Structures.SLE_Model_Grids.uniform_1d import Grid1D
from SLE_Model_Autoarray.SLE_Model_Structures.SLE_Model_Grids.uniform_2d import Grid2D
from SLE_Model_Autoarray.SLE_Model_Structures.SLE_Model_Grids.irregular_2d import (
    Grid2DIrregular,
)

Grid1D2DLike = Union[(np.ndarray, Grid1D, Grid2D, Grid2DIrregular)]
Grid2DLike = Union[(np.ndarray, Grid2D, Grid2DIrregular)]
from SLE_Model_Autoarray.SLE_Model_Structures.SLE_Model_Arrays.irregular import (
    ArrayIrregular,
)
from SLE_Model_Autoarray.SLE_Model_Structures.visibilities import Visibilities
from SLE_Model_Autoarray.SLE_Model_Structures.visibilities import VisibilitiesNoiseMap

DataLike = Union[
    (np.ndarray, Array1D, Array2D, ArrayIrregular, Visibilities, VisibilitiesNoiseMap)
]
from SLE_Model_Autoarray.SLE_Model_Operators.transformer import TransformerDFT
from SLE_Model_Autoarray.SLE_Model_Operators.transformer import TransformerNUFFT

Transformer = Union[(TransformerDFT, TransformerNUFFT)]
from SLE_Model_Autoarray.SLE_Model_Layout.region import Region1D
from SLE_Model_Autoarray.SLE_Model_Layout.region import Region2D

Region1DLike = Union[(Region1D, Tuple[(int, int)])]
Region1DList = Union[(List[Region1D], List[Tuple[(int, int)]])]
Region2DLike = Union[(Region2D, Tuple[(int, int, int, int)])]
Region2DList = Union[(List[Region2D], List[Tuple[(int, int, int, int)]])]
