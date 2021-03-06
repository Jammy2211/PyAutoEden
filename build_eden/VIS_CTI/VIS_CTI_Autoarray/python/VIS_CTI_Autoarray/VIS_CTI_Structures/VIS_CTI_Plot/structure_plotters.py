import numpy as np
from typing import List, Union
from VIS_CTI_Autoarray.VIS_CTI_Plot.abstract_plotters import Plotter
from VIS_CTI_Autoarray.VIS_CTI_Plot.VIS_CTI_MatWrap.visuals import Visuals1D
from VIS_CTI_Autoarray.VIS_CTI_Plot.VIS_CTI_MatWrap.visuals import Visuals2D
from VIS_CTI_Autoarray.VIS_CTI_Plot.VIS_CTI_MatWrap.include import Include1D
from VIS_CTI_Autoarray.VIS_CTI_Plot.VIS_CTI_MatWrap.include import Include2D
from VIS_CTI_Autoarray.VIS_CTI_Plot.VIS_CTI_MatWrap.mat_plot import MatPlot1D
from VIS_CTI_Autoarray.VIS_CTI_Plot.VIS_CTI_MatWrap.mat_plot import MatPlot2D
from VIS_CTI_Autoarray.VIS_CTI_Plot.VIS_CTI_MatWrap.mat_plot import AutoLabels
from VIS_CTI_Autoarray.VIS_CTI_Structures.VIS_CTI_Arrays.VIS_CTI_OneD.array_1d import (
    Array1D,
)
from VIS_CTI_Autoarray.VIS_CTI_Structures.VIS_CTI_Arrays.VIS_CTI_TwoD.array_2d import (
    Array2D,
)
from VIS_CTI_Autoarray.VIS_CTI_Structures.VIS_CTI_Grids.VIS_CTI_TwoD.grid_2d import (
    Grid2D,
)


class Array2DPlotter(Plotter):
    def __init__(
        self,
        array,
        mat_plot_2d=MatPlot2D(),
        visuals_2d=Visuals2D(),
        include_2d=Include2D(),
    ):
        """
        Plots `Array2D` objects using the matplotlib method `imshow()` and many other matplotlib functions which 
        customize the plot's appearance.

        The `mat_plot_2d` attribute wraps matplotlib function calls to make the figure. By default, the settings
        passed to every matplotlib function called are those specified in the `config/visualize/mat_wrap/*.ini` files,
        but a user can manually input values into `MatPlot2d` to customize the figure's appearance.

        Overlaid on the figure are visuals, contained in the `Visuals2D` object. Attributes may be extracted from
        the `Array2D` and plotted via the visuals object, if the corresponding entry is `True` in the `Include2D`
        object or the `config/visualize/include.ini` file.

        Parameters
        ----------
        array
            The 2D array the plotter plot.
        mat_plot_2d
            Contains objects which wrap the matplotlib function calls that make 2D plots.
        visuals_2d
            Contains 2D visuals that can be overlaid on 2D plots.
        include_2d
            Specifies which attributes of the `Array2D` are extracted and plotted as visuals for 2D plots.
        """
        super().__init__(
            visuals_2d=visuals_2d, include_2d=include_2d, mat_plot_2d=mat_plot_2d
        )
        self.array = array

    def get_visuals_2d(self):
        return self.get_2d.via_mask_from(mask=self.array.mask)

    def figure_2d(self):
        """
        Plots the plotter's `Array2D` object in 2D.
        """
        self.mat_plot_2d.plot_array(
            array=self.array,
            visuals_2d=self.get_visuals_2d(),
            auto_labels=AutoLabels(title="Array2D", filename="array"),
        )


class Grid2DPlotter(Plotter):
    def __init__(
        self,
        grid,
        mat_plot_2d=MatPlot2D(),
        visuals_2d=Visuals2D(),
        include_2d=Include2D(),
    ):
        """
        Plots `Grid2D` objects using the matplotlib method `scatter()` and many other matplotlib functions which 
        customize the plot's appearance.

        The `mat_plot_2d` attribute wraps matplotlib function calls to make the figure. By default, the settings
        passed to every matplotlib function called are those specified in the `config/visualize/mat_wrap/*.ini` files,
        but a user can manually input values into `MatPlot2d` to customize the figure's appearance.

        Overlaid on the figure are visuals, contained in the `Visuals2D` object. Attributes may be extracted from
        the `Grid2D` and plotted via the visuals object, if the corresponding entry is `True` in the `Include2D`
        object or the `config/visualize/include.ini` file.

        Parameters
        ----------
        grid
            The 2D grid the plotter plot.
        mat_plot_2d
            Contains objects which wrap the matplotlib function calls that make 2D plots.
        visuals_2d
            Contains 2D visuals that can be overlaid on 2D plots.
        include_2d
            Specifies which attributes of the `Grid2D` are extracted and plotted as visuals for 2D plots.
        """
        super().__init__(
            visuals_2d=visuals_2d, include_2d=include_2d, mat_plot_2d=mat_plot_2d
        )
        self.grid = grid

    def get_visuals_2d(self):
        return self.get_2d.via_grid_from(grid=self.grid)

    def figure_2d(self, color_array=None):
        """
        Plots the plotter's `Grid2D` object in 2D.

        Parameters
        ----------
        color_array
            An array of RGB color values which can be used to give the plotted 2D grid a colorscale (w/ colorbar).
        """
        self.mat_plot_2d.plot_grid(
            grid=self.grid,
            visuals_2d=self.get_visuals_2d(),
            auto_labels=AutoLabels(title="Grid2D", filename="grid"),
            color_array=color_array,
        )


class YX1DPlotter(Plotter):
    def __init__(
        self,
        y,
        x,
        mat_plot_1d=MatPlot1D(),
        visuals_1d=Visuals1D(),
        include_1d=Include1D(),
    ):
        """
        Plots two 1D objects using the matplotlib method `plot()` (or a similar method) and many other matplotlib 
        functions which customize the plot's appearance.

        The `mat_plot_1d` attribute wraps matplotlib function calls to make the figure. By default, the settings
        passed to every matplotlib function called are those specified in the `config/visualize/mat_wrap/*.ini` files,
        but a user can manually input values into `MatPlot1d` to customize the figure's appearance.

        Overlaid on the figure are visuals, contained in the `Visuals1D` object. Attributes may be extracted from
        the `Array1D` and plotted via the visuals object, if the corresponding entry is `True` in the `Include1D`
        object or the `config/visualize/include.ini` file.

        Parameters
        ----------
        y
            The 1D y values the plotter plot.
        x
            The 1D x values the plotter plot.
        mat_plot_1d
            Contains objects which wrap the matplotlib function calls that make 1D plots.
        visuals_1d
            Contains 1D visuals that can be overlaid on 1D plots.
        include_1d
            Specifies which attributes of the `Array1D` are extracted and plotted as visuals for 1D plots.
        """
        super().__init__(
            visuals_1d=visuals_1d, include_1d=include_1d, mat_plot_1d=mat_plot_1d
        )
        self.y = y
        self.x = x

    def get_visuals_1d(self):
        return self.get_1d.via_array_1d_from(array_1d=self.x)

    def figure_1d(self):
        """
        Plots the plotter's y and x values in 1D.
        """
        self.mat_plot_1d.plot_yx(
            y=self.y,
            x=self.x,
            visuals_1d=self.get_visuals_1d(),
            auto_labels=AutoLabels(),
        )
