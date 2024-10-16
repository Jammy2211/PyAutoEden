import copy
from typing import Callable, Optional
from SLE_Model_Autoarray.SLE_Model_Plot.SLE_Model_Visuals.two_d import Visuals2D
from SLE_Model_Autoarray.SLE_Model_Plot.SLE_Model_Include.two_d import Include2D
from SLE_Model_Autoarray.SLE_Model_Plot.SLE_Model_MatPlot.two_d import MatPlot2D
from SLE_Model_Autoarray.SLE_Model_Plot.auto_labels import AutoLabels
from SLE_Model_Autoarray.SLE_Model_Plot.abstract_plotters import Plotter
from SLE_Model_Autoarray.SLE_Model_Dataset.SLE_Model_Imaging.dataset import Imaging


class ImagingPlotterMeta(Plotter):
    def __init__(
        self,
        dataset,
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
        dataset
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
        self.dataset = dataset
        self.get_visuals_2d = get_visuals_2d

    @property
    def imaging(self):
        return self.dataset

    def figures_2d(
        self,
        data=False,
        noise_map=False,
        psf=False,
        signal_to_noise_map=False,
        over_sampling=False,
        over_sampling_non_uniform=False,
        over_sampling_pixelization=False,
        title_str=None,
    ):
        """
        Plots the individual attributes of the plotter's `Imaging` object in 2D.

        The API is such that every plottable attribute of the `Imaging` object is an input parameter of type bool of
        the function, which if switched to `True` means that it is plotted.

        Parameters
        ----------
        data
            Whether to make a 2D plot (via `imshow`) of the image data.
        noise_map
            Whether to make a 2D plot (via `imshow`) of the noise map.
        psf
            Whether to make a 2D plot (via `imshow`) of the psf.
        signal_to_noise_map
            Whether to make a 2D plot (via `imshow`) of the signal-to-noise map.
        over_sampling
            Whether to make a 2D plot (via `imshow`) of the Over Sampling for input light profiles. If
            adaptive sub size is used, the sub size grid for a centre of (0.0, 0.0) is used.
        over_sampling_pixelization
            Whether to make a 2D plot (via `imshow`) of the Over Sampling for pixelizations.
        """
        if data:
            self.mat_plot_2d.plot_array(
                array=self.dataset.data,
                visuals_2d=self.get_visuals_2d(),
                auto_labels=AutoLabels(title=(title_str or f" Data"), filename="data"),
            )
        if noise_map:
            self.mat_plot_2d.plot_array(
                array=self.dataset.noise_map,
                visuals_2d=self.get_visuals_2d(),
                auto_labels=AutoLabels(
                    (title_str or f"Noise-Map"), filename="noise_map"
                ),
            )
        if psf:
            self.mat_plot_2d.plot_array(
                array=self.dataset.psf,
                visuals_2d=self.get_visuals_2d(),
                auto_labels=AutoLabels(
                    title=(title_str or f"Point Spread Function"),
                    filename="psf",
                    cb_unit="",
                ),
            )
        if signal_to_noise_map:
            self.mat_plot_2d.plot_array(
                array=self.dataset.signal_to_noise_map,
                visuals_2d=self.get_visuals_2d(),
                auto_labels=AutoLabels(
                    title=(title_str or f"Signal-To-Noise Map"),
                    filename="signal_to_noise_map",
                    cb_unit="",
                ),
            )
        if over_sampling:
            if self.dataset.over_sampling.uniform is None:
                from SLE_Model_Autoarray.SLE_Model_Operators.SLE_Model_OverSampling.uniform import (
                    OverSamplingUniform,
                )

                over_sampling = OverSamplingUniform.from_adaptive_scheme(
                    grid=self.dataset.grids.uniform,
                    name="PlotExample",
                    centre=(0.0, 0.0),
                )
                title = title_str or f"Over Sampling (Adaptive)"
            else:
                over_sampling = self.dataset.over_sampling.uniform
                title = title_str or f"Over Sampling"
            over_sampler = over_sampling.over_sampler_from(mask=self.dataset.mask)
            self.mat_plot_2d.plot_array(
                array=over_sampler.sub_size,
                visuals_2d=self.get_visuals_2d(),
                auto_labels=AutoLabels(
                    title=title, filename="over_sampling", cb_unit=""
                ),
            )
        if over_sampling_non_uniform:
            if self.dataset.over_sampling.non_uniform is not None:
                self.mat_plot_2d.plot_array(
                    array=self.dataset.grids.over_sampler_non_uniform.sub_size,
                    visuals_2d=self.get_visuals_2d(),
                    auto_labels=AutoLabels(
                        title=(title_str or f"Over Sampling (Non Uniform)"),
                        filename="over_sampling_non_uniform",
                        cb_unit="",
                    ),
                )
        if over_sampling_pixelization:
            self.mat_plot_2d.plot_array(
                array=self.dataset.grids.over_sampler_pixelization.sub_size,
                visuals_2d=self.get_visuals_2d(),
                auto_labels=AutoLabels(
                    title=(title_str or f"Over Sampling (Pixelization)"),
                    filename="over_sampling_pixelization",
                    cb_unit="",
                ),
            )

    def subplot(
        self,
        data=False,
        noise_map=False,
        psf=False,
        signal_to_noise_map=False,
        over_sampling=False,
        over_sampling_pixelization=False,
        auto_filename="subplot_dataset",
    ):
        """
        Plots the individual attributes of the plotter's `Imaging` object in 2D on a subplot.

        The API is such that every plottable attribute of the `Imaging` object is an input parameter of type bool of
        the function, which if switched to `True` means that it is included on the subplot.

        Parameters
        ----------
        data
            Whether to include a 2D plot (via `imshow`) of the image data.
        noise_map
            Whether to include a 2D plot (via `imshow`) of the noise map.
        psf
            Whether to include a 2D plot (via `imshow`) of the psf.
        signal_to_noise_map
            Whether to include a 2D plot (via `imshow`) of the signal-to-noise map.
        over_sampling
            Whether to include a 2D plot (via `imshow`) of the Over Sampling. If adaptive sub size is used, the
            sub size grid for a centre of (0.0, 0.0) is used.
        over_sampling_pixelization
            Whether to include a 2D plot (via `imshow`) of the Over Sampling for pixelizations.
        auto_filename
            The default filename of the output subplot if written to hard-disk.
        """
        self._subplot_custom_plot(
            data=data,
            noise_map=noise_map,
            psf=psf,
            signal_to_noise_map=signal_to_noise_map,
            over_sampling=over_sampling,
            over_sampling_pixelization=over_sampling_pixelization,
            auto_labels=AutoLabels(filename=auto_filename),
        )

    def subplot_dataset(self):
        """
        Standard subplot of the attributes of the plotter's `Imaging` object.
        """
        use_log10_original = self.mat_plot_2d.use_log10
        self.open_subplot_figure(number_subplots=9)
        self.figures_2d(data=True)
        contour_original = copy.copy(self.mat_plot_2d.contour)
        self.mat_plot_2d.use_log10 = True
        self.mat_plot_2d.contour = False
        self.figures_2d(data=True)
        self.mat_plot_2d.use_log10 = False
        self.mat_plot_2d.contour = contour_original
        self.figures_2d(noise_map=True)
        self.figures_2d(psf=True)
        self.mat_plot_2d.use_log10 = True
        self.figures_2d(psf=True)
        self.mat_plot_2d.use_log10 = False
        self.figures_2d(signal_to_noise_map=True)
        self.figures_2d(over_sampling=True)
        self.figures_2d(over_sampling_non_uniform=True)
        self.figures_2d(over_sampling_pixelization=True)
        self.mat_plot_2d.output.subplot_to_figure(auto_filename="subplot_dataset")
        self.close_subplot_figure()
        self.mat_plot_2d.use_log10 = use_log10_original


class ImagingPlotter(Plotter):
    def __init__(
        self,
        dataset,
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
        self.dataset = dataset
        self._imaging_meta_plotter = ImagingPlotterMeta(
            dataset=self.dataset,
            get_visuals_2d=self.get_visuals_2d,
            mat_plot_2d=self.mat_plot_2d,
            include_2d=self.include_2d,
            visuals_2d=self.visuals_2d,
        )
        self.figures_2d = self._imaging_meta_plotter.figures_2d
        self.subplot = self._imaging_meta_plotter.subplot
        self.subplot_dataset = self._imaging_meta_plotter.subplot_dataset

    def get_visuals_2d(self):
        return self.get_2d.via_mask_from(mask=self.dataset.mask)
