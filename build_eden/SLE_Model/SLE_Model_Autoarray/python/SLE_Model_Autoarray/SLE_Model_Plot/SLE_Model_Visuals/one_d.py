import numpy as np
from typing import List, Optional, Union
from SLE_Model_Autoarray.SLE_Model_Mask.mask_1d import Mask1D
from SLE_Model_Autoarray.SLE_Model_Plot.SLE_Model_Include.one_d import Include1D
from SLE_Model_Autoarray.SLE_Model_Plot.SLE_Model_Visuals.abstract import (
    AbstractVisuals,
)
from SLE_Model_Autoarray.SLE_Model_Structures.SLE_Model_Arrays.uniform_1d import Array1D
from SLE_Model_Autoarray.SLE_Model_Structures.SLE_Model_Grids.uniform_1d import Grid1D


class Visuals1D(AbstractVisuals):
    def __init__(
        self,
        origin=None,
        mask=None,
        points=None,
        vertical_line=None,
        shaded_region=None,
    ):
        self.origin = origin
        self.mask = mask
        self.points = points
        self.vertical_line = vertical_line
        self.shaded_region = shaded_region

    @property
    def include(self):
        return Include1D()

    def plot_via_plotter(self, plotter):
        if self.points is not None:
            plotter.yx_scatter.scatter_yx(y=self.points, x=np.arange(len(self.points)))
        if self.vertical_line is not None:
            plotter.vertical_line_axvline.axvline_vertical_line(
                vertical_line=self.vertical_line
            )
