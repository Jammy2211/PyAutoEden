import matplotlib.pyplot as plt
import numpy as np
from typing import List, Union
from SLE_Model_Autoarray.SLE_Model_Plot.SLE_Model_Wrap.SLE_Model_OneD.abstract import (
    AbstractMatWrap1D,
)
from SLE_Model_Autoarray.SLE_Model_Structures.SLE_Model_Arrays.uniform_1d import Array1D


class FillBetween(AbstractMatWrap1D):
    def __init__(self, match_color_to_yx=True, **kwargs):
        """
        Fills between two lines on a 1D plot of y versus x using the method `plt.fill_between`.

        This method is typically called after `plot_y_vs_x` to add a shaded region to the figure.

        This object wraps the following Matplotlib methods:

        - plt.fill_between: https://matplotlib.org/3.3.2/api/_as_gen/matplotlib.pyplot.fill_between.html

        Parameters
        ----------
        match_color_to_yx
            If True, the color of the shaded region is automatically matched to that of the yx line that is plotted,
            irrespective of the user inputs.
        """
        super().__init__(**kwargs)
        self.match_color_to_yx = match_color_to_yx

    def fill_between_shaded_regions(self, x, y1, y2):
        """
        Fill in between two lines `y1` and `y2` on a plot of y vs x.

        Parameters
        ----------
        x
            The xdata that is plotted.
        y1
            The first line of ydata that defines the region that is filled in.
        y1
            The second line of ydata that defines the region that is filled in.
        """
        config_dict = self.config_dict
        if self.match_color_to_yx:
            config_dict["color"] = plt.gca().lines[(-1)].get_color()
        plt.fill_between(x=x, y1=y1, y2=y2, **config_dict)
