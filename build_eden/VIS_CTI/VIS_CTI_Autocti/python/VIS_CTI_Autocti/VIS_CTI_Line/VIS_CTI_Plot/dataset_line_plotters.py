import numpy as np
import VIS_CTI_Autoarray.VIS_CTI_Plot as aplt
from VIS_CTI_Autoarray.VIS_CTI_Plot.VIS_CTI_MatWrap.mat_plot import AutoLabels
from VIS_CTI_Autocti.VIS_CTI_Plot.abstract_plotters import Plotter
from VIS_CTI_Autocti.VIS_CTI_Line.dataset import DatasetLine


class DatasetLinePlotter(Plotter):
    def __init__(
        self,
        dataset_line,
        mat_plot_1d=aplt.MatPlot1D(),
        visuals_1d=aplt.Visuals1D(),
        include_1d=aplt.Include1D(),
    ):
        """
        Plots the attributes of `DatasetLine` objects using the matplotlib method `line()` and many other matplotlib
        functions which customize the plot's appearance.

        The `mat_plot_1d` attribute wraps matplotlib function calls to make the figure. By default, the settings
        passed to every matplotlib function called are those specified in the `config/visualize/mat_wrap/*.ini` files,
        but a user can manually input values into `MatPlot1d` to customize the figure's appearance.

        Overlaid on the figure are visuals, contained in the `Visuals1D` object. Attributes may be extracted from
        the `Imaging` and plotted via the visuals object, if the corresponding entry is `True` in the `Include1D`
        object or the `config/visualize/include.ini` file.

        Parameters
        ----------
        imaging
            The charge injection line imaging dataset the plotter plots.
        mat_plot_1d
            Contains objects which wrap the matplotlib function calls that make 1D plots.
        visuals_1d
            Contains 1D visuals that can be overlaid on 1D plots.
        include_1d
            Specifies which attributes of the `ImagingCI` are extracted and plotted as visuals for 1D plots.
        """
        super().__init__(
            mat_plot_1d=mat_plot_1d, include_1d=include_1d, visuals_1d=visuals_1d
        )
        self.dataset_line = dataset_line

    def get_visuals_1d(self):
        return self.visuals_1d

    def figures_1d(
        self, data=False, noise_map=False, signal_to_noise_map=False, pre_cti_data=False
    ):
        """
        Plots the individual attributes of the plotter's `DatasetLine` object in 1D.

        The API is such that every plottable attribute of the `Imaging` object is an input parameter of type bool of
        the function, which if switched to `True` means that it is plotted.

        Parameters
        ----------
        image
            Whether or not to make a 1D plot (via `plot`) of the data.
        noise_map
            Whether or not to make a 1D plot (via `plot`) of the noise map.
        signal_to_noise_map
            Whether or not to make a 1D plot (via `plot`) of the signal-to-noise map.
        pre_cti_data
            Whether or not to make a 1D plot (via `plot`) of the pre-cti data.
        """
        if data:
            self.mat_plot_1d.plot_yx(
                y=self.dataset_line.data,
                x=np.arange(len(self.dataset_line.data)),
                visuals_1d=self.get_visuals_1d(),
                auto_labels=AutoLabels(title="Line Dataset Line", filename="data"),
            )
        if noise_map:
            self.mat_plot_1d.plot_yx(
                y=self.dataset_line.noise_map,
                x=np.arange(len(self.dataset_line.noise_map)),
                visuals_1d=self.get_visuals_1d(),
                auto_labels=AutoLabels(
                    title="Line Dataset Noise Map", filename="noise_map"
                ),
            )
        if signal_to_noise_map:
            self.mat_plot_1d.plot_yx(
                y=self.dataset_line.signal_to_noise_map,
                x=np.arange(len(self.dataset_line.signal_to_noise_map)),
                visuals_1d=self.get_visuals_1d(),
                auto_labels=AutoLabels(
                    title="Line Dataset Signal-To-Noise Map",
                    filename="signal_to_noise_map",
                ),
            )
        if pre_cti_data:
            self.mat_plot_1d.plot_yx(
                y=self.dataset_line.pre_cti_data,
                x=np.arange(len(self.dataset_line.pre_cti_data)),
                visuals_1d=self.get_visuals_1d(),
                auto_labels=AutoLabels(
                    title="Line Dataset Pre CTI Line", filename="pre_cti_data"
                ),
            )

    def subplot(
        self,
        data=False,
        noise_map=False,
        signal_to_noise_map=False,
        pre_cti_data=False,
        auto_filename="subplot_dataset_line",
    ):
        """
        Plots the individual attributes of the plotter's `DatasetLine` object in 1D on a subplot.

        The API is such that every plottable attribute of the `Imaging` object is an input parameter of type bool of
        the function, which if switched to `True` means that it is included on the subplot.

        Parameters
        ----------
        image
            Whether or not to include a 1D plot (via `plot`) of the data.
        noise_map
            Whether or not to include a 1D plot (via `plot`) of the noise map.
        signal_to_noise_map
            Whether or not to include a 1D plot (via `plot`) of the signal-to-noise map.
        pre_cti_data
            Whether or not to include a 1D plot (via `plot`) of the pre-cti data.
        """
        self._subplot_custom_plot(
            data=data,
            noise_map=noise_map,
            signal_to_noise_map=signal_to_noise_map,
            pre_cti_data=pre_cti_data,
            auto_labels=AutoLabels(filename=auto_filename),
        )

    def subplot_dataset_line(self):
        """
        Standard subplot of the attributes of the plotter's `DatasetLine` object.
        """
        self.subplot(
            data=True, noise_map=True, signal_to_noise_map=True, pre_cti_data=True
        )
