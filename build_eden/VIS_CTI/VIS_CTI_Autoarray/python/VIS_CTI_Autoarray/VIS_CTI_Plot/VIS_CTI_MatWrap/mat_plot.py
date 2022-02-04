from VIS_CTI_Autoarray.VIS_CTI_Plot.VIS_CTI_Wrap.wrap_base import set_backend

set_backend()
import matplotlib.pyplot as plt
import numpy as np
from typing import Iterable, Optional, List, Union
from VIS_CTI_Autoarray.VIS_CTI_Structures.VIS_CTI_Arrays.VIS_CTI_OneD.array_1d import (
    Array1D,
)
from VIS_CTI_Autoarray.VIS_CTI_Structures.VIS_CTI_Arrays.VIS_CTI_TwoD.array_2d import (
    Array2D,
)
from VIS_CTI_Autoarray.VIS_CTI_Inversion.VIS_CTI_Mappers.rectangular import (
    MapperRectangularNoInterp,
)
from VIS_CTI_Autoarray.VIS_CTI_Inversion.VIS_CTI_Mappers.delaunay import MapperDelaunay
from VIS_CTI_Autoarray.VIS_CTI_Inversion.VIS_CTI_Mappers.voronoi import (
    MapperVoronoiNoInterp,
)
from VIS_CTI_Autoarray.VIS_CTI_Inversion.VIS_CTI_Mappers.voronoi import MapperVoronoi
from VIS_CTI_Autoarray.VIS_CTI_Plot.VIS_CTI_MatWrap.visuals import Visuals1D
from VIS_CTI_Autoarray.VIS_CTI_Plot.VIS_CTI_MatWrap.visuals import Visuals2D
from VIS_CTI_Autoarray.VIS_CTI_Structures.VIS_CTI_Arrays.VIS_CTI_TwoD import (
    array_2d_util,
)
from VIS_CTI_Autoarray import exc
from VIS_CTI_Autoarray.VIS_CTI_Plot.VIS_CTI_Wrap import wrap_base as wb
from VIS_CTI_Autoarray.VIS_CTI_Plot.VIS_CTI_Wrap import wrap_1d as w1d
from VIS_CTI_Autoarray.VIS_CTI_Plot.VIS_CTI_Wrap import wrap_2d as w2d


class AutoLabels:
    def __init__(
        self, title=None, ylabel=None, xlabel=None, legend=None, filename=None
    ):
        self.title = title
        self.ylabel = ylabel
        self.xlabel = xlabel
        self.legend = legend
        self.filename = filename


class AbstractMatPlot:
    def __init__(
        self,
        units=None,
        figure=None,
        axis=None,
        cmap=None,
        colorbar=None,
        colorbar_tickparams=None,
        tickparams=None,
        yticks=None,
        xticks=None,
        title=None,
        ylabel=None,
        xlabel=None,
        text=None,
        legend=None,
        output=None,
    ):
        """
        Visualizes data structures (e.g an `Array2D`, `Grid2D`, `VectorField`, etc.) using Matplotlib.
        
        The `Plotter` is passed objects from the `wrap_base` package which wrap matplotlib plot functions and customize
        the appearance of the plots of the data structure. If the values of these matplotlib wrapper objects are not
        manually specified, they assume the default values provided in the `config.visualize.mat_*` `.ini` config files.
        
        The following data structures can be plotted using the following matplotlib functions:
        
        - `Array2D`:, using `plt.imshow`.
        - `Grid2D`: using `plt.scatter`.
        - `Line`: using `plt.plot`, `plt.semilogy`, `plt.loglog` or `plt.scatter`.
        - `VectorField`: using `plt.quiver`.
        - `RectangularMapper`: using `plt.imshow`.
        - `MapperVoronoiNoInterp`: using `plt.fill`.
        
        Parameters
        ----------
        units
            The units of the figure used to plot the data structure which sets the y and x ticks and labels.
        figure
            Opens the matplotlib figure before plotting via `plt.figure` and closes it once plotting is complete
            via `plt.close`
        axis
            Sets the extent of the figure axis via `plt.axis` and allows for a manual axis range.
        cmap
            Customizes the colormap of the plot and its normalization via matplotlib `colors` objects such 
            as `colors.Normalize` and `colors.LogNorm`.
        colorbar
            Plots the colorbar of the plot via `plt.colorbar` and customizes its tick labels and values using method
            like `cb.set_yticklabels`.
        colorbar_tickparams
            Customizes the yticks of the colorbar plotted via `plt.colorbar`.
        tickparams
            Customizes the appearances of the y and x ticks on the plot (e.g. the fontsize) using `plt.tick_params`.
        yticks
            Sets the yticks of the plot, including scaling them to new units depending on the `Units` object, via
            `plt.yticks`.
        xticks
            Sets the xticks of the plot, including scaling them to new units depending on the `Units` object, via
            `plt.xticks`.
        title
            Sets the figure title and customizes its appearance using `plt.title`.        
        ylabel
            Sets the figure ylabel and customizes its appearance using `plt.ylabel`.
        xlabel
            Sets the figure xlabel and customizes its appearance using `plt.xlabel`.
        legend
            Sets whether the plot inclues a legend and customizes its appearance and labels using `plt.legend`.
        output
            Sets if the figure is displayed on the user's screen or output to `.png` using `plt.show` and `plt.savefig`
        """
        self.units = units or wb.Units()
        self.figure = figure or wb.Figure()
        self.axis = axis or wb.Axis()
        self.cmap = cmap or wb.Cmap()
        self.colorbar = colorbar or wb.Colorbar()
        self.colorbar_tickparams = colorbar_tickparams or wb.ColorbarTickParams()
        self.tickparams = tickparams or wb.TickParams()
        self.yticks = yticks or wb.YTicks()
        self.xticks = xticks or wb.XTicks()
        self.title = title or wb.Title()
        self.ylabel = ylabel or wb.YLabel()
        self.xlabel = xlabel or wb.XLabel()
        self.text = text or wb.Text()
        self.legend = legend or wb.Legend()
        self.output = output or wb.Output()
        self.number_subplots = None
        self.subplot_shape = None
        self.subplot_index = None

    def set_for_subplot(self, is_for_subplot):
        """
        Sets the `is_for_subplot` attribute for every `MatWrap` object in this `MatPlot` object by updating
        the `is_for_subplot`. By changing this tag:

            - The [subplot] section of the config file of every `MatWrap` object is used instead of [figure].
            - Calls which output or close the matplotlib figure are over-ridden so that the subplot is not removed.

        Parameters
        ----------
        is_for_subplot
            The entry the `is_for_subplot` attribute of every `MatWrap` object is set too.
        """
        self.is_for_subplot = is_for_subplot
        self.output.bypass = is_for_subplot
        for (attr, value) in self.__dict__.items():
            if hasattr(value, "is_for_subplot"):
                value.is_for_subplot = is_for_subplot

    def get_subplot_rows_columns(self, number_subplots):
        """
        Get the size of a sub plotter in (total_y_pixels, total_x_pixels), based on the number of subplots that are
        going to be plotted.

        Parameters
        -----------
        number_subplots
            The number of subplots that are to be plotted in the figure.
        """
        if self.subplot_shape is not None:
            return self.subplot_shape
        if number_subplots <= 2:
            return (1, 2)
        elif number_subplots <= 4:
            return (2, 2)
        elif number_subplots <= 6:
            return (2, 3)
        elif number_subplots <= 9:
            return (3, 3)
        elif number_subplots <= 12:
            return (3, 4)
        elif number_subplots <= 16:
            return (4, 4)
        elif number_subplots <= 20:
            return (4, 5)
        else:
            return (6, 6)

    def setup_subplot(self, aspect=None, subplot_rows_columns=None):
        if subplot_rows_columns is None:
            (rows, columns) = self.get_subplot_rows_columns(
                number_subplots=self.number_subplots
            )
        else:
            rows = subplot_rows_columns[0]
            columns = subplot_rows_columns[1]
        if aspect is None:
            plt.subplot(rows, columns, self.subplot_index)
        else:
            plt.subplot(rows, columns, self.subplot_index, aspect=float(aspect))
        self.subplot_index += 1


class MatPlot1D(AbstractMatPlot):
    def __init__(
        self,
        units=None,
        figure=None,
        axis=None,
        cmap=None,
        colorbar=None,
        colorbar_tickparams=None,
        tickparams=None,
        yticks=None,
        xticks=None,
        title=None,
        ylabel=None,
        xlabel=None,
        text=None,
        legend=None,
        output=None,
        yx_plot=None,
        vertical_line_axvline=None,
        yx_scatter=None,
        fill_between=None,
    ):
        """
        Visualizes 1D data structures (e.g a `Line`, etc.) using Matplotlib.

        The `Plotter` is passed objects from the `wrap_base` package which wrap matplotlib plot functions and customize
        the appearance of the plots of the data structure. If the values of these matplotlib wrapper objects are not
        manually specified, they assume the default values provided in the `config.visualize.mat_*` `.ini` config files.

        The following 1D data structures can be plotted using the following matplotlib functions:

        - `Line` using `plt.plot`.

        Parameters
        ----------
        units
            The units of the figure used to plot the data structure which sets the y and x ticks and labels.
        figure
            Opens the matplotlib figure before plotting via `plt.figure` and closes it once plotting is complete
            via `plt.close`.
        axis
            Sets the extent of the figure axis via `plt.axis` and allows for a manual axis range.
        cmap
            Customizes the colormap of the plot and its normalization via matplotlib `colors` objects such 
            as `colors.Normalize` and `colors.LogNorm`.
        colorbar
            Plots the colorbar of the plot via `plt.colorbar` and customizes its tick labels and values using method
            like `cb.set_yticklabels`.
        colorbar_tickparams
            Customizes the yticks of the colorbar plotted via `plt.colorbar`.
        tickparams
            Customizes the appearances of the y and x ticks on the plot, (e.g. the fontsize), using `plt.tick_params`.
        yticks
            Sets the yticks of the plot, including scaling them to new units depending on the `Units` object, via
            `plt.yticks`.
        xticks
            Sets the xticks of the plot, including scaling them to new units depending on the `Units` object, via
            `plt.xticks`.
        title
            Sets the figure title and customizes its appearance using `plt.title`.        
        ylabel
            Sets the figure ylabel and customizes its appearance using `plt.ylabel`.
        xlabel
            Sets the figure xlabel and customizes its appearance using `plt.xlabel`.
        legend
            Sets whether the plot inclues a legend and customizes its appearance and labels using `plt.legend`.
        output
            Sets if the figure is displayed on the user's screen or output to `.png` using `plt.show` and `plt.savefig`
        yx_plot
            Sets how the y versus x plot appears, for example if it each axis is linear or log, using `plt.plot`.
        vertical_line_axvline
            Sets how a vertical line plotted on the figure using the `plt.axvline` method.
        """
        super().__init__(
            units=units,
            figure=figure,
            axis=axis,
            cmap=cmap,
            colorbar=colorbar,
            colorbar_tickparams=colorbar_tickparams,
            tickparams=tickparams,
            yticks=yticks,
            xticks=xticks,
            title=title,
            ylabel=ylabel,
            xlabel=xlabel,
            text=text,
            legend=legend,
            output=output,
        )
        self.yx_plot = yx_plot or w1d.YXPlot()
        self.vertical_line_axvline = vertical_line_axvline or w1d.AXVLine()
        self.yx_scatter = yx_scatter or w1d.YXScatter()
        self.fill_between = fill_between or w1d.FillBetween()
        self.is_for_multi_plot = False
        self.is_for_subplot = False

    def set_for_multi_plot(self, is_for_multi_plot, color):
        """
        Sets the `is_for_subplot` attribute for every `MatWrap` object in this `MatPlot` object by updating
        the `is_for_subplot`. By changing this tag:

            - The [subplot] section of the config file of every `MatWrap` object is used instead of [figure].
            - Calls which output or close the matplotlib figure are over-ridden so that the subplot is not removed.

        Parameters
        ----------
        is_for_subplot : bool
            The entry the `is_for_subplot` attribute of every `MatWrap` object is set too.
        """
        self.is_for_multi_plot = is_for_multi_plot
        self.output.bypass = is_for_multi_plot
        self.yx_plot.kwargs["c"] = color
        self.vertical_line_axvline.kwargs["c"] = color
        self.vertical_line_axvline.no_label = True

    def plot_yx(
        self,
        y,
        visuals_1d,
        auto_labels,
        x=None,
        plot_axis_type_override=None,
        y_errors=None,
        x_errors=None,
        bypass=False,
    ):
        if (y is None) or (np.count_nonzero(y) == 0):
            return
        if (not self.is_for_subplot) and (not self.is_for_multi_plot):
            self.figure.open()
        elif not bypass:
            if self.is_for_subplot:
                self.setup_subplot()
        self.title.set(auto_title=auto_labels.title)
        use_integers = False
        if x is None:
            x = np.arange(len(y))
            use_integers = True
        if self.yx_plot.plot_axis_type is None:
            plot_axis_type = "linear"
        else:
            plot_axis_type = self.yx_plot.plot_axis_type
        if plot_axis_type_override is not None:
            plot_axis_type = plot_axis_type_override
        self.yx_plot.plot_y_vs_x(
            y=y,
            x=x,
            label=auto_labels.legend,
            plot_axis_type=plot_axis_type,
            y_errors=y_errors,
            x_errors=x_errors,
        )
        if visuals_1d.shaded_region is not None:
            self.fill_between.fill_between_shaded_regions(
                x=x, y1=visuals_1d.shaded_region[0], y2=visuals_1d.shaded_region[1]
            )
        if "extent" in self.axis.config_dict:
            self.axis.set()
        self.ylabel.set(units=self.units, include_brackets=False)
        self.xlabel.set(units=self.units, include_brackets=False)
        self.tickparams.set()
        if plot_axis_type == "symlog":
            plt.yscale("symlog")
        self.xticks.set(
            array=None,
            min_value=np.min(x),
            max_value=np.max(x),
            units=self.units,
            use_integers=use_integers,
        )
        self.title.set(auto_title=auto_labels.title)
        self.ylabel.set(units=self.units, auto_label=auto_labels.ylabel)
        self.xlabel.set(units=self.units, auto_label=auto_labels.xlabel)
        self.text.set()
        visuals_1d.plot_via_plotter(plotter=self)
        if auto_labels.legend is not None:
            self.legend.set()
        if (not self.is_for_subplot) and (not self.is_for_multi_plot):
            self.output.to_figure(structure=None, auto_filename=auto_labels.filename)
            self.figure.close()


class MatPlot2D(AbstractMatPlot):
    def __init__(
        self,
        units=None,
        figure=None,
        axis=None,
        cmap=None,
        colorbar=None,
        colorbar_tickparams=None,
        tickparams=None,
        yticks=None,
        xticks=None,
        title=None,
        ylabel=None,
        xlabel=None,
        text=None,
        legend=None,
        output=None,
        array_overlay=None,
        grid_scatter=None,
        grid_plot=None,
        grid_errorbar=None,
        vector_yx_quiver=None,
        patch_overlay=None,
        delaunay_drawer=None,
        voronoi_drawer=None,
        voronoiNN_drawer=None,
        origin_scatter=None,
        mask_scatter=None,
        border_scatter=None,
        positions_scatter=None,
        index_scatter=None,
        pixelization_grid_scatter=None,
        parallel_overscan_plot=None,
        serial_prescan_plot=None,
        serial_overscan_plot=None,
    ):
        """
        Visualizes 2D data structures (e.g an `Array2D`, `Grid2D`, `VectorField`, etc.) using Matplotlib.

        The `Plotter` is passed objects from the `wrap` package which wrap matplotlib plot functions and customize
        the appearance of the plots of the data structure. If the values of these matplotlib wrapper objects are not
        manually specified, they assume the default values provided in the `config.visualize.mat_*` `.ini` config files.

        The following 2D data structures can be plotted using the following matplotlib functions:

        - `Array2D`:, using `plt.imshow`.
        - `Grid2D`: using `plt.scatter`.
        - `Line`: using `plt.plot`, `plt.semilogy`, `plt.loglog` or `plt.scatter`.
        - `VectorField`: using `plt.quiver`.
        - `RectangularMapper`: using `plt.imshow`.
        - `MapperVoronoiNoInterp`: using `plt.fill`.

        Parameters
        ----------
        units
            The units of the figure used to plot the data structure which sets the y and x ticks and labels.
        figure
            Opens the matplotlib figure before plotting via `plt.figure` and closes it once plotting is complete
            via `plt.close`.
        axis
            Sets the extent of the figure axis via `plt.axis` and allows for a manual axis range.
        cmap
            Customizes the colormap of the plot and its normalization via matplotlib `colors` objects such 
            as `colors.Normalize` and `colors.LogNorm`.
        colorbar
            Plots the colorbar of the plot via `plt.colorbar` and customizes its tick labels and values using method
            like `cb.set_yticklabels`.
        colorbar_tickparams
            Customizes the yticks of the colorbar plotted via `plt.colorbar`.
        tickparams
            Customizes the appearances of the y and x ticks on the plot, (e.g. the fontsize), using `plt.tick_params`.
        yticks
            Sets the yticks of the plot, including scaling them to new units depending on the `Units` object, via
            `plt.yticks`.
        xticks
            Sets the xticks of the plot, including scaling them to new units depending on the `Units` object, via
            `plt.xticks`.
        title
            Sets the figure title and customizes its appearance using `plt.title`.        
        ylabel
            Sets the figure ylabel and customizes its appearance using `plt.ylabel`.
        xlabel
            Sets the figure xlabel and customizes its appearance using `plt.xlabel`.
        legend
            Sets whether the plot inclues a legend and customizes its appearance and labels using `plt.legend`.
        output
            Sets if the figure is displayed on the user's screen or output to `.png` using `plt.show` and `plt.savefig`
        array_overlay
            Overlays an input `Array2D` over the figure using `plt.imshow`.
        grid_scatter
            Scatters a `Grid2D` of (y,x) coordinates over the figure using `plt.scatter`.
        grid_plot
            Plots lines of data (e.g. a y versus x plot via `plt.plot`, vertical lines via `plt.avxline`, etc.)
        vector_yx_quiver
            Plots a `VectorField` object using the matplotlib function `plt.quiver`.
        patch_overlay
            Overlays matplotlib `patches.Patch` objects over the figure, such as an `Ellipse`.
        voronoi_drawer
            Draws a colored Voronoi mesh of pixels using `plt.fill`.
        delaunay_drawer
            Draws a colored Delaunay mesh of pixels using `plt.fill`.
        origin_scatter
            Scatters the (y,x) origin of the data structure on the figure.
        mask_scatter
            Scatters an input `Mask2d` over the plotted data structure's figure.
        border_scatter
            Scatters the border of an input `Mask2d` over the plotted data structure's figure.
        positions_scatter
            Scatters specific (y,x) coordinates input as a `Grid2DIrregular` object over the figure.
        index_scatter
            Scatters specific coordinates of an input `Grid2D` based on input values of the `Grid2D`'s 1D or 2D indexes.
        pixelization_grid_scatter
            Scatters the `PixelizationGrid` of a `Pixelization` object.
        parallel_overscan_plot
            Plots the parallel overscan on an `Array2D` data structure representing a CCD imaging via `plt.plot`.
        serial_prescan_plot
            Plots the serial prescan on an `Array2D` data structure representing a CCD imaging via `plt.plot`.
        serial_overscan_plot
            Plots the serial overscan on an `Array2D` data structure representing a CCD imaging via `plt.plot`.
        """
        super().__init__(
            units=units,
            figure=figure,
            axis=axis,
            cmap=cmap,
            colorbar=colorbar,
            colorbar_tickparams=colorbar_tickparams,
            tickparams=tickparams,
            yticks=yticks,
            xticks=xticks,
            title=title,
            ylabel=ylabel,
            xlabel=xlabel,
            text=text,
            legend=legend,
            output=output,
        )
        self.array_overlay = array_overlay or w2d.ArrayOverlay()
        self.grid_scatter = grid_scatter or w2d.GridScatter()
        self.grid_plot = grid_plot or w2d.GridPlot()
        self.grid_errorbar = grid_errorbar or w2d.GridErrorbar()
        self.vector_yx_quiver = vector_yx_quiver or w2d.VectorYXQuiver()
        self.patch_overlay = patch_overlay or w2d.PatchOverlay()
        self.delaunay_drawer = delaunay_drawer or w2d.DelaunayDrawer()
        self.voronoi_drawer = voronoi_drawer or w2d.VoronoiDrawer()
        self.voronoiNN_drawer = voronoiNN_drawer or w2d.VoronoiNNDrawer()
        self.origin_scatter = origin_scatter or w2d.OriginScatter()
        self.mask_scatter = mask_scatter or w2d.MaskScatter()
        self.border_scatter = border_scatter or w2d.BorderScatter()
        self.positions_scatter = positions_scatter or w2d.PositionsScatter()
        self.index_scatter = index_scatter or w2d.IndexScatter()
        self.pixelization_grid_scatter = (
            pixelization_grid_scatter or w2d.PixelizationGridScatter()
        )
        self.parallel_overscan_plot = (
            parallel_overscan_plot or w2d.ParallelOverscanPlot()
        )
        self.serial_prescan_plot = serial_prescan_plot or w2d.SerialPrescanPlot()
        self.serial_overscan_plot = serial_overscan_plot or w2d.SerialOverscanPlot()
        self.is_for_subplot = False

    def plot_array(self, array, visuals_2d, auto_labels, bypass=False):
        """
        Plot an `Array2D` data structure as a figure using the matplotlib wrapper objects and tools.

        This `Array2D` is plotted using `plt.imshow`.

        Parameters
        -----------
        array
            The 2D array of data_type which is plotted.
        visuals_2d
            Contains all the visuals that are plotted over the `Array2D` (e.g. the origin, mask, grids, etc.).
        bypass
            If `True`, `plt.close` is omitted and the matplotlib figure remains open. This is used when making subplots.
        """
        if (array is None) or np.all((array == 0)):
            return
        if (array.pixel_scales is None) and self.units.use_scaled:
            raise exc.ArrayException(
                "You cannot plot an array using its scaled unit_label if the input array does not have a pixel scales attribute."
            )
        array = array.binned
        if array.mask.is_all_false:
            buffer = 0
        else:
            buffer = 1
        if array.zoom_for_plot:
            extent = array.extent_of_zoomed_array(buffer=buffer)
            array = array.zoomed_around_mask(buffer=buffer)
        else:
            extent = array.extent
        if not self.is_for_subplot:
            self.figure.open()
        elif not bypass:
            self.setup_subplot()
        aspect = self.figure.aspect_from(shape_native=array.shape_native)
        norm_scale = self.cmap.norm_from(array=array)
        plt.imshow(
            X=array.native,
            aspect=aspect,
            cmap=self.cmap.config_dict["cmap"],
            norm=norm_scale,
            extent=extent,
        )
        if visuals_2d.array_overlay is not None:
            self.array_overlay.overlay_array(
                array=visuals_2d.array_overlay, figure=self.figure
            )
        extent_axis = self.axis.config_dict.get("extent")
        if extent_axis is None:
            extent_axis = extent
        self.axis.set(extent=extent_axis)
        self.tickparams.set()
        self.yticks.set(
            array=array,
            min_value=extent_axis[2],
            max_value=extent_axis[3],
            units=self.units,
        )
        self.xticks.set(
            array=array,
            min_value=extent_axis[0],
            max_value=extent_axis[1],
            units=self.units,
        )
        self.title.set(auto_title=auto_labels.title)
        self.ylabel.set(units=self.units, include_brackets=True)
        self.xlabel.set(units=self.units, include_brackets=True)
        self.text.set()
        if self.colorbar is not None:
            cb = self.colorbar.set()
            self.colorbar_tickparams.set(cb=cb)
        grid_indexes = None
        if (visuals_2d.indexes is not None) or (visuals_2d.pix_indexes is not None):
            grid_indexes = array.mask.masked_grid
        visuals_2d.plot_via_plotter(plotter=self, grid_indexes=grid_indexes)
        if (not self.is_for_subplot) and (not bypass):
            self.output.to_figure(structure=array, auto_filename=auto_labels.filename)
            self.figure.close()

    def plot_grid(
        self,
        grid,
        visuals_2d,
        auto_labels,
        color_array=None,
        y_errors=None,
        x_errors=None,
        buffer=1.0,
    ):
        """Plot a grid of (y,x) Cartesian coordinates as a scatter plotter of points.

        Parameters
        -----------
        grid
            The (y,x) coordinates of the grid, in an array of shape (total_coordinates, 2).
        indexes
            A set of points that are plotted in a different colour for emphasis (e.g. to show the mappings between             different planes).
        """
        if not self.is_for_subplot:
            self.figure.open()
        else:
            self.setup_subplot()
        if color_array is None:
            if (y_errors is None) and (x_errors is None):
                self.grid_scatter.scatter_grid(grid=grid)
            else:
                self.grid_errorbar.errorbar_grid(
                    grid=grid, y_errors=y_errors, x_errors=x_errors
                )
        elif color_array is not None:
            cmap = plt.get_cmap(self.cmap.config_dict["cmap"])
            if (y_errors is None) and (x_errors is None):
                self.grid_scatter.scatter_grid_colored(
                    grid=grid, color_array=color_array, cmap=cmap
                )
            else:
                self.grid_errorbar.errorbar_grid_colored(
                    grid=grid,
                    cmap=cmap,
                    color_array=color_array,
                    y_errors=y_errors,
                    x_errors=x_errors,
                )
            if self.colorbar is not None:
                colorbar = self.colorbar.set_with_color_values(
                    cmap=self.cmap.config_dict["cmap"], color_values=color_array
                )
                if (colorbar is not None) and (self.colorbar_tickparams is not None):
                    self.colorbar_tickparams.set(cb=colorbar)
        self.title.set(auto_title=auto_labels.title)
        self.ylabel.set(units=self.units, include_brackets=True)
        self.xlabel.set(units=self.units, include_brackets=True)
        self.text.set()
        extent = self.axis.config_dict.get("extent")
        if extent is None:
            extent = grid.extent + (buffer * grid.extent)
        self.axis.set(extent=extent, grid=grid)
        self.tickparams.set()
        if not self.axis.symmetric_around_centre:
            self.yticks.set(
                array=None, min_value=extent[2], max_value=extent[3], units=self.units
            )
            self.xticks.set(
                array=None, min_value=extent[0], max_value=extent[1], units=self.units
            )
        visuals_2d.plot_via_plotter(plotter=self, grid_indexes=grid)
        if not self.is_for_subplot:
            self.output.to_figure(structure=grid, auto_filename=auto_labels.filename)
            self.figure.close()

    def plot_mapper(
        self, mapper, visuals_2d, auto_labels, source_pixelilzation_values=None
    ):
        if isinstance(mapper, MapperRectangularNoInterp):
            self._plot_rectangular_mapper(
                mapper=mapper,
                visuals_2d=visuals_2d,
                auto_labels=auto_labels,
                source_pixelilzation_values=source_pixelilzation_values,
            )
        elif isinstance(mapper, MapperDelaunay):
            self._plot_delaunay_mapper(
                mapper=mapper,
                visuals_2d=visuals_2d,
                auto_labels=auto_labels,
                source_pixelilzation_values=source_pixelilzation_values,
            )
        elif isinstance(mapper, MapperVoronoi):
            self._plot_voronoiNN_mapper(
                mapper=mapper,
                visuals_2d=visuals_2d,
                auto_labels=auto_labels,
                source_pixelilzation_values=source_pixelilzation_values,
            )
        else:
            self._plot_voronoi_mapper(
                mapper=mapper,
                visuals_2d=visuals_2d,
                auto_labels=auto_labels,
                source_pixelilzation_values=source_pixelilzation_values,
            )

    def _plot_rectangular_mapper(
        self, mapper, visuals_2d, auto_labels, source_pixelilzation_values=None
    ):
        if source_pixelilzation_values is not None:
            solution_array_2d = array_2d_util.array_2d_native_from(
                array_2d_slim=source_pixelilzation_values,
                mask_2d=np.full(
                    fill_value=False, shape=mapper.source_pixelization_grid.shape_native
                ),
                sub_size=1,
            )
            source_pixelilzation_values = Array2D.manual(
                array=solution_array_2d,
                sub_size=1,
                pixel_scales=mapper.source_pixelization_grid.pixel_scales,
                origin=mapper.source_pixelization_grid.origin,
            )
        extent = self.axis.config_dict.get("extent")
        extent = (
            extent if (extent is not None) else mapper.source_pixelization_grid.extent
        )
        aspect_inv = self.figure.aspect_for_subplot_from(extent=extent)
        if not self.is_for_subplot:
            self.figure.open()
        else:
            self.setup_subplot(aspect=aspect_inv)
        if source_pixelilzation_values is not None:
            self.plot_array(
                array=source_pixelilzation_values,
                visuals_2d=visuals_2d,
                auto_labels=auto_labels,
                bypass=True,
            )
        self.axis.set(extent=extent, grid=mapper.source_pixelization_grid)
        self.yticks.set(
            array=None, min_value=extent[2], max_value=extent[3], units=self.units
        )
        self.xticks.set(
            array=None, min_value=extent[0], max_value=extent[1], units=self.units
        )
        self.text.set()
        self.grid_plot.plot_rectangular_grid_lines(
            extent=mapper.source_pixelization_grid.extent,
            shape_native=mapper.shape_native,
        )
        self.title.set(auto_title=auto_labels.title)
        self.tickparams.set()
        self.ylabel.set(units=self.units, include_brackets=True)
        self.xlabel.set(units=self.units, include_brackets=True)
        visuals_2d.plot_via_plotter(
            plotter=self, grid_indexes=mapper.source_grid_slim, mapper=mapper
        )
        if not self.is_for_subplot:
            self.output.to_figure(structure=None, auto_filename=auto_labels.filename)
            self.figure.close()

    def _plot_voronoi_mapper(
        self, mapper, visuals_2d, auto_labels, source_pixelilzation_values=None
    ):
        extent = self.axis.config_dict.get("extent")
        extent = (
            extent if (extent is not None) else mapper.source_pixelization_grid.extent
        )
        aspect_inv = self.figure.aspect_for_subplot_from(extent=extent)
        if not self.is_for_subplot:
            self.figure.open()
        else:
            self.setup_subplot(aspect=aspect_inv)
        self.axis.set(extent=extent, grid=mapper.source_pixelization_grid)
        plt.gca().set_aspect(aspect_inv)
        self.tickparams.set()
        self.yticks.set(
            array=None, min_value=extent[2], max_value=extent[3], units=self.units
        )
        self.xticks.set(
            array=None, min_value=extent[0], max_value=extent[1], units=self.units
        )
        self.text.set()
        self.voronoi_drawer.draw_voronoi_pixels(
            mapper=mapper,
            values=source_pixelilzation_values,
            cmap=self.cmap,
            colorbar=self.colorbar,
            colorbar_tickparams=self.colorbar_tickparams,
        )
        self.title.set(auto_title=auto_labels.title)
        self.ylabel.set(units=self.units, include_brackets=True)
        self.xlabel.set(units=self.units, include_brackets=True)
        visuals_2d.plot_via_plotter(
            plotter=self, grid_indexes=mapper.source_grid_slim, mapper=mapper
        )
        if not self.is_for_subplot:
            self.output.to_figure(structure=None, auto_filename=auto_labels.filename)
            self.figure.close()

    def _plot_delaunay_mapper(
        self, mapper, visuals_2d, auto_labels, source_pixelilzation_values=None
    ):
        extent = self.axis.config_dict.get("extent")
        extent = (
            extent if (extent is not None) else mapper.source_pixelization_grid.extent
        )
        aspect_inv = self.figure.aspect_for_subplot_from(extent=extent)
        if not self.is_for_subplot:
            self.figure.open()
        else:
            self.setup_subplot(aspect=aspect_inv)
        self.axis.set(extent=extent, grid=mapper.source_pixelization_grid)
        self.tickparams.set()
        self.yticks.set(
            array=None, min_value=extent[2], max_value=extent[3], units=self.units
        )
        self.xticks.set(
            array=None, min_value=extent[0], max_value=extent[1], units=self.units
        )
        self.text.set()
        self.delaunay_drawer.draw_delaunay_pixels(
            mapper=mapper,
            values=source_pixelilzation_values,
            cmap=self.cmap,
            colorbar=self.colorbar,
            colorbar_tickparams=self.colorbar_tickparams,
            aspect=aspect_inv,
        )
        self.title.set(auto_title=auto_labels.title)
        self.ylabel.set(units=self.units, include_brackets=True)
        self.xlabel.set(units=self.units, include_brackets=True)
        visuals_2d.plot_via_plotter(
            plotter=self, grid_indexes=mapper.source_grid_slim, mapper=mapper
        )
        if not self.is_for_subplot:
            self.output.to_figure(structure=None, auto_filename=auto_labels.filename)
            self.figure.close()

    def _plot_voronoiNN_mapper(
        self, mapper, visuals_2d, auto_labels, source_pixelilzation_values=None
    ):
        extent = self.axis.config_dict.get("extent")
        extent = (
            extent if (extent is not None) else mapper.source_pixelization_grid.extent
        )
        aspect_inv = self.figure.aspect_for_subplot_from(extent=extent)
        if not self.is_for_subplot:
            self.figure.open()
        else:
            self.setup_subplot(aspect=aspect_inv)
        self.axis.set(extent=extent, grid=mapper.source_pixelization_grid)
        self.tickparams.set()
        self.yticks.set(
            array=None, min_value=extent[2], max_value=extent[3], units=self.units
        )
        self.xticks.set(
            array=None, min_value=extent[0], max_value=extent[1], units=self.units
        )
        self.text.set()
        self.voronoiNN_drawer.draw_voronoiNN_pixels(
            mapper=mapper,
            values=source_pixelilzation_values,
            cmap=self.cmap,
            colorbar=self.colorbar,
            colorbar_tickparams=self.colorbar_tickparams,
            aspect=aspect_inv,
        )
        self.title.set(auto_title=auto_labels.title)
        self.ylabel.set(units=self.units, include_brackets=True)
        self.xlabel.set(units=self.units, include_brackets=True)
        visuals_2d.plot_via_plotter(
            plotter=self, grid_indexes=mapper.source_grid_slim, mapper=mapper
        )
        if not self.is_for_subplot:
            self.output.to_figure(structure=None, auto_filename=auto_labels.filename)
            self.figure.close()
