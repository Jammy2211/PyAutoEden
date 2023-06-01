import numpy as np
from typing import List, Union, Optional
import SLE_Model_Autoarray as aa
import SLE_Model_Autoarray.SLE_Model_Plot as aplt


class Visuals1D(aplt.Visuals1D):
    def __init__(
        self,
        origin=None,
        mask=None,
        points=None,
        vertical_line=None,
        shaded_region=None,
        half_light_radius=None,
        half_light_radius_errors=None,
        einstein_radius=None,
        einstein_radius_errors=None,
        model_fluxes=None,
    ):
        super().__init__(
            origin=origin,
            mask=mask,
            points=points,
            vertical_line=vertical_line,
            shaded_region=shaded_region,
        )
        self.half_light_radius = half_light_radius
        self.half_light_radius_errors = half_light_radius_errors
        self.einstein_radius = einstein_radius
        self.einstein_radius_errors = einstein_radius_errors
        self.model_fluxes = model_fluxes

    def plot_via_plotter(self, plotter, grid_indexes=None, mapper=None):
        super().plot_via_plotter(plotter=plotter)
        if self.half_light_radius is not None:
            plotter.half_light_radius_axvline.axvline_vertical_line(
                vertical_line=self.half_light_radius,
                vertical_errors=self.half_light_radius_errors,
                label="Half-light Radius",
            )
        if self.einstein_radius is not None:
            plotter.einstein_radius_axvline.axvline_vertical_line(
                vertical_line=self.einstein_radius,
                vertical_errors=self.einstein_radius_errors,
                label="Einstein Radius",
            )
        if self.model_fluxes is not None:
            plotter.model_fluxes_yx_scatter.scatter_yx(
                y=self.model_fluxes, x=np.arange(len(self.model_fluxes))
            )
