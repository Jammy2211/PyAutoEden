from VIS_CTI_Autoarray.VIS_CTI_Plot.VIS_CTI_Wrap.wrap_base import set_backend

set_backend()
from VIS_CTI_Autoarray.VIS_CTI_Plot.abstract_plotters import AbstractPlotter
from VIS_CTI_Autocti.VIS_CTI_Plot.get_visuals import GetVisuals1D
from VIS_CTI_Autocti.VIS_CTI_Plot.get_visuals import GetVisuals2D


class Plotter(AbstractPlotter):
    @property
    def get_1d(self):
        return GetVisuals1D(visuals=self.visuals_1d, include=self.include_1d)

    @property
    def get_2d(self):
        return GetVisuals2D(visuals=self.visuals_2d, include=self.include_2d)
