from SLE_Model_Autoarray.SLE_Model_Plot.SLE_Model_Wrap.SLE_Model_Base.abstract import (
    set_backend,
)

set_backend()
from SLE_Model_Autoarray.SLE_Model_Plot.abstract_plotters import AbstractPlotter


class Plotter(AbstractPlotter):
    @property
    def get_1d(self):
        from SLE_Model_Autogalaxy.SLE_Model_Plot.SLE_Model_GetVisuals.one_d import (
            GetVisuals1D,
        )

        return GetVisuals1D(visuals=self.visuals_1d, include=self.include_1d)

    @property
    def get_2d(self):
        from SLE_Model_Autogalaxy.SLE_Model_Plot.SLE_Model_GetVisuals.two_d import (
            GetVisuals2D,
        )

        return GetVisuals2D(visuals=self.visuals_2d, include=self.include_2d)
