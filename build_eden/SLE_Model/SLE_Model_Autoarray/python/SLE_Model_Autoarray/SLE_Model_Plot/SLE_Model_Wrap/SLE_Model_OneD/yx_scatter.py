import matplotlib.pyplot as plt
import numpy as np
from typing import Union
from SLE_Model_Autoarray.SLE_Model_Plot.SLE_Model_Wrap.SLE_Model_OneD.abstract import (
    AbstractMatWrap1D,
)
from SLE_Model_Autoarray.SLE_Model_Structures.SLE_Model_Grids.uniform_1d import Grid1D


class YXScatter(AbstractMatWrap1D):
    def __init__(self, **kwargs):
        """
        Scatters a 1D set of points on a 1D plot. Unlike the `YXPlot` object these are scattered over an existing plot.

        This object wraps the following Matplotlib methods:

        - plt.scatter: https://matplotlib.org/3.1.1/api/_as_gen/matplotlib.pyplot.scatter.html
        """
        super().__init__(**kwargs)

    def scatter_yx(self, y, x):
        """
        Plot an input grid of (y,x) coordinates using the matplotlib method `plt.scatter`.

        Parameters
        ----------
        grid
            The points that are
        errors
            The error on every point of the grid that is plotted.
        """
        config_dict = self.config_dict
        if len(config_dict["c"]) > 1:
            config_dict["c"] = config_dict["c"][0]
        plt.scatter(y=y, x=x, **config_dict)
