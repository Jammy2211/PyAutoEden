from typing import Callable
from VIS_CTI_Autoarray.VIS_CTI_Plot.VIS_CTI_MatWrap.visuals import Visuals2D
from VIS_CTI_Autoarray.VIS_CTI_Plot.VIS_CTI_MatWrap.include import Include2D
from VIS_CTI_Autoarray.VIS_CTI_Plot.VIS_CTI_MatWrap.mat_plot import MatPlot2D
from VIS_CTI_Autoarray.VIS_CTI_Plot.VIS_CTI_MatWrap.mat_plot import AutoLabels
from VIS_CTI_Autoarray.VIS_CTI_Plot.abstract_plotters import Plotter
from VIS_CTI_Autoarray.VIS_CTI_Dataset.imaging import Imaging


class ImagingPlotterMeta(Plotter):
    def __init__(
        self,
        imaging,
        get_visuals_2d,
        mat_plot_2d=MatPlot2D(),
        visuals_2d=Visuals2D(),
        include_2d=Include2D(),
    ):
        """
        Plots the attributes of `Imaging` objects using the matplotlib method `imshow()` and many other matplotlib
        functions which customize the plot's appearance.

        The `mat_plot_2d` attribute wraps matplotlib function calls to make the figure. By default, the settings
        passed to every matplotlib function called are those specified in the `config/visualize/mat_wrap/*.ini` files,
        but a user can manually input values into `MatPlot2d` to customize the figure's appearance.

        Overlaid on the figure are visuals, contained in the `Visuals2D` object. Attributes may be extracted from
        the `Imaging` and plotted via the visuals object, if the corresponding entry is `True` in the `Include2D`
        object or the `config/visualize/include.ini` file.

        Parameters
        ----------
        imaging
            The imaging dataset the plotter plots.
        get_visuals_2d
            A function which extracts from the `Imaging` the 2D visuals which are plotted on figures.
        mat_plot_2d
            Contains objects which wrap the matplotlib function calls that make 2D plots.
        visuals_2d
            Contains 2D visuals that can be overlaid on 2D plots.
        include_2d
            Specifies which attributes of the `Imaging` are extracted and plotted as visuals for 2D plots.
        """
        super().__init__(
            mat_plot_2d=mat_plot_2d, include_2d=include_2d, visuals_2d=visuals_2d
        )
        self.imaging = imaging
        self.get_visuals_2d = get_visuals_2d

    def figures_2d(
        self,
        image=False,
        noise_map=False,
        psf=False,
        inverse_noise_map=False,
        signal_to_noise_map=False,
        absolute_signal_to_noise_map=False,
        potential_chi_squared_map=False,
    ):
        """
        Plots the individual attributes of the plotter's `Imaging` object in 2D.

        The API is such that every plottable attribute of the `Imaging` object is an input parameter of type bool of
        the function, which if switched to `True` means that it is plotted.

        Parameters
        ----------
        image
            Whether or not to make a 2D plot (via `imshow`) of the image data.
        noise_map
            Whether or not to make a 2D plot (via `imshow`) of the noise map.
        psf
            Whether or not to make a 2D plot (via `imshow`) of the psf.
        inverse_noise_map
            Whether or not to make a 2D plot (via `imshow`) of the inverse noise map.
        signal_to_noise_map
            Whether or not to make a 2D plot (via `imshow`) of the signal-to-noise map.
        absolute_signal_to_noise_map
            Whether or not to make a 2D plot (via `imshow`) of the absolute signal to noise map.
        potential_chi_squared_map
            Whether or not to make a 2D plot (via `imshow`) of the potential chi squared map.
        """
        if image:
            self.mat_plot_2d.plot_array(
                array=self.imaging.image,
                visuals_2d=self.get_visuals_2d(),
                auto_labels=AutoLabels(title="Image", filename="image_2d"),
            )
        if noise_map:
            self.mat_plot_2d.plot_array(
                array=self.imaging.noise_map,
                visuals_2d=self.get_visuals_2d(),
                auto_labels=AutoLabels("Noise-Map", filename="noise_map"),
            )
        if psf:
            self.mat_plot_2d.plot_array(
                array=self.imaging.psf,
                visuals_2d=self.get_visuals_2d(),
                auto_labels=AutoLabels(title="Point Spread Function", filename="psf"),
            )
        if inverse_noise_map:
            self.mat_plot_2d.plot_array(
                array=self.imaging.inverse_noise_map,
                visuals_2d=self.get_visuals_2d(),
                auto_labels=AutoLabels(
                    title="Inverse Noise-Map", filename="inverse_noise_map"
                ),
            )
        if signal_to_noise_map:
            self.mat_plot_2d.plot_array(
                array=self.imaging.signal_to_noise_map,
                visuals_2d=self.get_visuals_2d(),
                auto_labels=AutoLabels(
                    title="Signal-To-Noise Map", filename="signal_to_noise_map"
                ),
            )
        if absolute_signal_to_noise_map:
            self.mat_plot_2d.plot_array(
                array=self.imaging.absolute_signal_to_noise_map,
                visuals_2d=self.get_visuals_2d(),
                auto_labels=AutoLabels(
                    title="Absolute Signal-To-Noise Map",
                    filename="absolute_signal_to_noise_map",
                ),
            )
        if potential_chi_squared_map:
            self.mat_plot_2d.plot_array(
                array=self.imaging.potential_chi_squared_map,
                visuals_2d=self.get_visuals_2d(),
                auto_labels=AutoLabels(
                    title="Potential Chi-Squared Map",
                    filename="potential_chi_squared_map",
                ),
            )

    def subplot(
        self,
        image=False,
        noise_map=False,
        psf=False,
        signal_to_noise_map=False,
        inverse_noise_map=False,
        absolute_signal_to_noise_map=False,
        potential_chi_squared_map=False,
        auto_filename="subplot_imaging",
    ):
        """
        Plots the individual attributes of the plotter's `Imaging` object in 2D on a subplot.

        The API is such that every plottable attribute of the `Imaging` object is an input parameter of type bool of
        the function, which if switched to `True` means that it is included on the subplot.

        Parameters
        ----------
        image
            Whether or not to include a 2D plot (via `imshow`) of the image data.
        noise_map
            Whether or not to include a 2D plot (via `imshow`) of the noise map.
        psf
            Whether or not to include a 2D plot (via `imshow`) of the psf.
        inverse_noise_map
            Whether or not to include a 2D plot (via `imshow`) of the inverse noise map.
        signal_to_noise_map
            Whether or not to include a 2D plot (via `imshow`) of the signal-to-noise map.
        absolute_signal_to_noise_map
            Whether or not to include a 2D plot (via `imshow`) of the absolute signal to noise map.
        potential_chi_squared_map
            Whether or not to include a 2D plot (via `imshow`) of the potential chi squared map.
        auto_filename
            The default filename of the output subplot if written to hard-disk.
        """
        self._subplot_custom_plot(
            image=image,
            noise_map=noise_map,
            psf=psf,
            signal_to_noise_map=signal_to_noise_map,
            inverse_noise_map=inverse_noise_map,
            absolute_signal_to_noise_map=absolute_signal_to_noise_map,
            potential_chi_squared_map=potential_chi_squared_map,
            auto_labels=AutoLabels(filename=auto_filename),
        )

    def subplot_imaging(self):
        """
        Standard subplot of the attributes of the plotter's `Imaging` object.
        """
        self.subplot(
            image=True,
            noise_map=True,
            psf=True,
            signal_to_noise_map=True,
            inverse_noise_map=True,
            potential_chi_squared_map=True,
        )


class ImagingPlotter(Plotter):
    def __init__(
        self,
        imaging,
        mat_plot_2d=MatPlot2D(),
        visuals_2d=Visuals2D(),
        include_2d=Include2D(),
    ):
        """
        Plots the attributes of `Imaging` objects using the matplotlib method `imshow()` and many other matplotlib
        functions which customize the plot's appearance.

        The `mat_plot_2d` attribute wraps matplotlib function calls to make the figure. By default, the settings
        passed to every matplotlib function called are those specified in the `config/visualize/mat_wrap/*.ini` files,
        but a user can manually input values into `MatPlot2d` to customize the figure's appearance.

        Overlaid on the figure are visuals, contained in the `Visuals2D` object. Attributes may be extracted from
        the `Imaging` and plotted via the visuals object, if the corresponding entry is `True` in the `Include2D`
        object or the `config/visualize/include.ini` file.

        Parameters
        ----------
        imaging
            The imaging dataset the plotter plots.
        mat_plot_2d
            Contains objects which wrap the matplotlib function calls that make 2D plots.
        visuals_2d
            Contains 2D visuals that can be overlaid on 2D plots.
        include_2d
            Specifies which attributes of the `Imaging` are extracted and plotted as visuals for 2D plots.
        """
        super().__init__(
            mat_plot_2d=mat_plot_2d, include_2d=include_2d, visuals_2d=visuals_2d
        )
        self.imaging = imaging
        self._imaging_meta_plotter = ImagingPlotterMeta(
            imaging=self.imaging,
            get_visuals_2d=self.get_visuals_2d,
            mat_plot_2d=self.mat_plot_2d,
            include_2d=self.include_2d,
            visuals_2d=self.visuals_2d,
        )
        self.figures_2d = self._imaging_meta_plotter.figures_2d
        self.subplot = self._imaging_meta_plotter.subplot
        self.subplot_imaging = self._imaging_meta_plotter.subplot_imaging

    def get_visuals_2d(self):
        return self.get_2d.via_mask_from(mask=self.imaging.mask)
