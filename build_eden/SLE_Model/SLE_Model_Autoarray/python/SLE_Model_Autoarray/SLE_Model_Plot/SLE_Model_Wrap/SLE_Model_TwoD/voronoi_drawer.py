import matplotlib.pyplot as plt
import numpy as np
from typing import Optional
from SLE_Model_Autoarray.SLE_Model_Plot.SLE_Model_Wrap.SLE_Model_TwoD.abstract import (
    AbstractMatWrap2D,
)
from SLE_Model_Autoarray.SLE_Model_Plot.SLE_Model_Wrap.SLE_Model_Base.units import Units
from SLE_Model_Autoarray.SLE_Model_Inversion.SLE_Model_Pixelization.SLE_Model_Mappers.voronoi import (
    MapperVoronoi,
)
from SLE_Model_Autoarray.SLE_Model_Inversion.SLE_Model_Pixelization.SLE_Model_Mesh import (
    mesh_util,
)
from SLE_Model_Autoarray.SLE_Model_Plot.SLE_Model_Wrap import SLE_Model_Base as wb


class VoronoiDrawer(AbstractMatWrap2D):
    """
    Draws Voronoi pixels from a `MapperVoronoi` object (see `inversions.mapper`). This includes both drawing
    each Voronoi cell and coloring it according to a color value.

    The mapper contains the grid of (y,x) coordinate where the centre of each Voronoi cell is plotted.

    This object wraps methods described in below:

    https://matplotlib.org/3.3.2/api/_as_gen/matplotlib.pyplot.fill.html
    """

    def draw_voronoi_pixels(
        self,
        mapper,
        pixel_values,
        units,
        cmap,
        colorbar,
        colorbar_tickparams=None,
        ax=None,
        use_log10=False,
    ):
        """
        Draws the Voronoi pixels of the input `mapper` using its `mesh_grid` which contains the (y,x)
        coordinate of the centre of every Voronoi cell. This uses the method `plt.fill`.

        Parameters
        ----------
        mapper
            A mapper object which contains the Voronoi mesh.
        pixel_values
            An array used to compute the color values that every Voronoi cell is plotted using.
        cmap
            The colormap used to plot each Voronoi cell.
        colorbar
            The `Colorbar` object in `mat_base` used to set the colorbar of the figure the Voronoi mesh is plotted on.
        colorbar_tickparams
            The `ColorbarTickParams` object in `mat_base` used to set the tick labels of the colorbar.
        ax
            The matplotlib axis the Voronoi mesh is plotted on.
        use_log10
            If `True`, the colorbar is plotted using a log10 scale.
        """
        if ax is None:
            ax = plt.gca()
        (regions, vertices) = mesh_util.voronoi_revised_from(voronoi=mapper.voronoi)
        if pixel_values is not None:
            norm = cmap.norm_from(array=pixel_values, use_log10=use_log10)
            if use_log10:
                pixel_values[(pixel_values < 0.0001)] = 0.0001
                pixel_values = np.log10(pixel_values)
            vmin = cmap.vmin_from(array=pixel_values, use_log10=use_log10)
            vmax = cmap.vmax_from(array=pixel_values, use_log10=use_log10)
            color_values = np.where((pixel_values > vmax), vmax, pixel_values)
            color_values = np.where((pixel_values < vmin), vmin, color_values)
            if vmax != vmin:
                color_array = (color_values - vmin) / (vmax - vmin)
            else:
                color_array = np.ones(color_values.shape[0])
            cmap = plt.get_cmap(cmap.cmap)
            if colorbar is not None:
                cb = colorbar.set_with_color_values(
                    units=units,
                    norm=norm,
                    cmap=cmap,
                    color_values=color_values,
                    ax=ax,
                    use_log10=use_log10,
                )
                if (cb is not None) and (colorbar_tickparams is not None):
                    colorbar_tickparams.set(cb=cb)
        else:
            cmap = plt.get_cmap("Greys")
            color_array = np.zeros(shape=mapper.pixels)
        for (region, index) in zip(regions, range(mapper.pixels)):
            polygon = vertices[region]
            color = cmap(color_array[index])
            plt.fill(*zip(*polygon), facecolor=color, zorder=(-1), **self.config_dict)
