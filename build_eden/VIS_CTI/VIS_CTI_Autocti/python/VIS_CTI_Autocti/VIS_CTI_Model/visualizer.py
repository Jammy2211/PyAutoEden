from os import path
from VIS_CTI_Autoconf import conf
from VIS_CTI_Autoarray.VIS_CTI_Plot.VIS_CTI_Wrap.wrap_base import Output
from VIS_CTI_Autoarray.VIS_CTI_Plot.VIS_CTI_MatWrap.mat_plot import MatPlot1D
from VIS_CTI_Autoarray.VIS_CTI_Plot.VIS_CTI_MatWrap.mat_plot import MatPlot2D
from VIS_CTI_Autoarray.VIS_CTI_Plot.VIS_CTI_MatWrap.include import Include1D
from VIS_CTI_Autoarray.VIS_CTI_Plot.VIS_CTI_MatWrap.include import Include2D


def setting(section, name):
    return conf.instance["visualize"]["plots"][section][name]


def plot_setting(section, name):
    return setting(section, name)


class Visualizer:
    def __init__(self, visualize_path):
        self.visualize_path = visualize_path
        self.include_1d = Include1D()
        self.include_2d = Include2D()

    def mat_plot_1d_from(self, subfolders, format="png"):
        return MatPlot1D(
            output=Output(
                path=path.join(self.visualize_path, subfolders), format=format
            )
        )

    def mat_plot_2d_from(self, subfolders, format="png"):
        return MatPlot2D(
            output=Output(
                path=path.join(self.visualize_path, subfolders), format=format
            )
        )
