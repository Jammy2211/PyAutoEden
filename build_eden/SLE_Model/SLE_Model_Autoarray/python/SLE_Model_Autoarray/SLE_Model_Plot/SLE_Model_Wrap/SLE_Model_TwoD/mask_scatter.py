from SLE_Model_Autoarray.SLE_Model_Plot.SLE_Model_Wrap.SLE_Model_TwoD.grid_scatter import (
    GridScatter,
)


class MaskScatter(GridScatter):
    """
    Plots a mask over an image, using the `Mask2d` object's (y,x) `edge` property.

    See `wrap.base.Scatter` for a description of how matplotlib is wrapped to make this plot.
    """
