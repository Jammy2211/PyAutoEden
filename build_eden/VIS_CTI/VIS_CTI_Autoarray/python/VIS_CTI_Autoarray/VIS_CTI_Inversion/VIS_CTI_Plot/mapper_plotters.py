import numpy as np
from typing import Union
from VIS_CTI_Autoarray.VIS_CTI_Plot.abstract_plotters import Plotter
from VIS_CTI_Autoarray.VIS_CTI_Plot.VIS_CTI_MatWrap.visuals import Visuals2D
from VIS_CTI_Autoarray.VIS_CTI_Plot.VIS_CTI_MatWrap.include import Include2D
from VIS_CTI_Autoarray.VIS_CTI_Plot.VIS_CTI_MatWrap.mat_plot import MatPlot2D
from VIS_CTI_Autoarray.VIS_CTI_Plot.VIS_CTI_MatWrap.mat_plot import AutoLabels
from VIS_CTI_Autoarray.VIS_CTI_Structures.VIS_CTI_Arrays.VIS_CTI_TwoD.array_2d import (
    Array2D,
)
from VIS_CTI_Autoarray.VIS_CTI_Inversion.VIS_CTI_Mappers.rectangular import (
    MapperRectangularNoInterp,
)
from VIS_CTI_Autoarray.VIS_CTI_Inversion.VIS_CTI_Mappers.voronoi import (
    MapperVoronoiNoInterp,
)


class MapperPlotter(Plotter):
    def __init__(
        self,
        mapper,
        mat_plot_2d=MatPlot2D(),
        visuals_2d=Visuals2D(),
        include_2d=Include2D(),
    ):
        """
        Plots the attributes of `Mapper` objects using the matplotlib method `imshow()` and many other matplotlib
        functions which customize the plot's appearance.

        The `mat_plot_2d` attribute wraps matplotlib function calls to make the figure. By default, the settings
        passed to every matplotlib function called are those specified in the `config/visualize/mat_wrap/*.ini` files,
        but a user can manually input values into `MatPlot2d` to customize the figure's appearance.

        Overlaid on the figure are visuals, contained in the `Visuals2D` object. Attributes may be extracted from
        the `Mapper` and plotted via the visuals object, if the corresponding entry is `True` in the `Include2D`
        object or the `config/visualize/include.ini` file.

        Parameters
        ----------
        mapper
            The mapper the plotter plots.
        mat_plot_2d
            Contains objects which wrap the matplotlib function calls that make 2D plots.
        visuals_2d
            Contains 2D visuals that can be overlaid on 2D plots.
        include_2d
            Specifies which attributes of the `Mapper` are extracted and plotted as visuals for 2D plots.
        """
        super().__init__(
            visuals_2d=visuals_2d, include_2d=include_2d, mat_plot_2d=mat_plot_2d
        )
        self.mapper = mapper

    def get_visuals_2d_for_data(self):
        return self.get_2d.via_mapper_for_data_from(mapper=self.mapper)

    def get_visuals_2d_for_source(self):
        return self.get_2d.via_mapper_for_source_from(mapper=self.mapper)

    def figure_2d(self, solution_vector=None):
        """
        Plots the plotter's `Mapper` object in 2D.

        Parameters
        ----------
        solution_vector
            A vector of values which can culor the pixels of the mapper's source pixels.
        """
        self.mat_plot_2d.plot_mapper(
            mapper=self.mapper,
            visuals_2d=self.get_2d.via_mapper_for_source_from(mapper=self.mapper),
            source_pixelilzation_values=solution_vector,
            auto_labels=AutoLabels(title="Mapper", filename="mapper"),
        )

    def subplot_image_and_mapper(self, image):
        """
        Make a subplot of an input image and the `Mapper`'s source-plane reconstruction.

        This function can include colored points that mark the mappings between the image pixels and their
        corresponding locations in the `Mapper` source-plane and reconstruction. This therefore visually illustrates
        the mapping process.

        Parameters
        ----------
        image
            The image which is plotted on the subplot.
        """
        self.open_subplot_figure(number_subplots=2)
        self.mat_plot_2d.plot_array(
            array=image,
            visuals_2d=self.get_visuals_2d_for_data(),
            auto_labels=AutoLabels(title="Image"),
        )
        if self.visuals_2d.pix_indexes is not None:
            indexes = self.mapper.pix_indexes_for_slim_indexes(
                pix_indexes=self.visuals_2d.pix_indexes
            )
            self.mat_plot_2d.index_scatter.scatter_grid_indexes(
                grid=self.mapper.source_grid_slim.mask.masked_grid, indexes=indexes
            )
        self.figure_2d()
        self.mat_plot_2d.output.subplot_to_figure(
            auto_filename="subplot_image_and_mapper"
        )
        self.close_subplot_figure()

    def plot_source_from(self, source_pixelization_values, auto_labels):
        """
        Plot the source of the `Mapper` where the coloring is specified by an input set of values.

        Parameters
        ----------
        source_pixelization_values
            The values of the mapper's source pixels used for coloring the figure.
        auto_labels
            The labels given to the figure.
        """
        self.mat_plot_2d.plot_mapper(
            mapper=self.mapper,
            visuals_2d=self.get_visuals_2d_for_source(),
            auto_labels=auto_labels,
            source_pixelilzation_values=source_pixelization_values,
        )
