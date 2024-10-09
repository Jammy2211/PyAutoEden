from SLE_Model_Autoarray.SLE_Model_Plot.abstract_plotters import AbstractPlotter
import SLE_Model_Autogalaxy.SLE_Model_Plot as aplt
from SLE_Model_Autolens.SLE_Model_Point.SLE_Model_Fit.dataset import FitPointDataset


class FitPointDatasetPlotter(AbstractPlotter):
    def __init__(
        self,
        fit,
        mat_plot_1d=aplt.MatPlot1D(),
        visuals_1d=aplt.Visuals1D(),
        include_1d=aplt.Include1D(),
        mat_plot_2d=aplt.MatPlot2D(),
        visuals_2d=aplt.Visuals2D(),
        include_2d=aplt.Include2D(),
    ):
        super().__init__(
            mat_plot_1d=mat_plot_1d,
            visuals_1d=visuals_1d,
            include_1d=include_1d,
            mat_plot_2d=mat_plot_2d,
            include_2d=include_2d,
            visuals_2d=visuals_2d,
        )
        self.fit = fit

    def get_visuals_1d(self):
        return self.visuals_1d

    def get_visuals_2d(self):
        return self.visuals_2d

    def figures_2d(self, positions=False, fluxes=False):
        if positions:
            visuals_2d = self.get_visuals_2d()
            visuals_2d += visuals_2d.__class__(positions=self.fit.positions.model_data)
            self.mat_plot_2d.plot_grid(
                grid=self.fit.dataset.positions,
                y_errors=self.fit.dataset.positions_noise_map,
                x_errors=self.fit.dataset.positions_noise_map,
                visuals_2d=visuals_2d,
                auto_labels=aplt.AutoLabels(
                    title=f"{self.fit.dataset.name} Fit Positions",
                    filename="fit_point_dataset_positions",
                ),
                buffer=0.1,
            )
        if (self.mat_plot_1d.subplot_index is not None) and (
            self.mat_plot_2d.subplot_index is not None
        ):
            self.mat_plot_1d.subplot_index = max(
                self.mat_plot_1d.subplot_index, self.mat_plot_2d.subplot_index
            )
        if fluxes:
            if self.fit.dataset.fluxes is not None:
                visuals_1d = self.get_visuals_1d()
                visuals_1d += visuals_1d.__class__(
                    model_fluxes=self.fit.flux.model_fluxes
                )
                self.mat_plot_1d.plot_yx(
                    y=self.fit.dataset.fluxes,
                    y_errors=self.fit.dataset.fluxes_noise_map,
                    visuals_1d=visuals_1d,
                    auto_labels=aplt.AutoLabels(
                        title=f" {self.fit.dataset.name} Fit Fluxes",
                        filename="fit_point_dataset_fluxes",
                        xlabel="Point Number",
                    ),
                    plot_axis_type_override="errorbar",
                )

    def subplot(self, positions=False, fluxes=False, auto_filename="subplot_fit"):
        self._subplot_custom_plot(
            positions=positions,
            fluxes=fluxes,
            auto_labels=aplt.AutoLabels(filename=auto_filename),
        )

    def subplot_fit(self):
        self.subplot(positions=True, fluxes=True)
