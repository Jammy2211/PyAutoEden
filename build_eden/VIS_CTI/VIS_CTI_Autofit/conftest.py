import os
from os import path
from os.path import dirname
import pytest
from matplotlib import pyplot

from VIS_CTI_Autoconf import conf
from VIS_CTI_Autofit import fixtures

directory = path.abspath(dirname(__file__))


@pytest.fixture(autouse=True)
def set_config_path(request):

    conf.instance.push(
        new_path=path.join(
            directory, "../VIS_CTI_Programs/auxdir/VIS_CTI_Programs/config"
        ),
        output_path=path.join(directory, "output"),
    )


@pytest.fixture(name="test_directory", scope="session")
def make_test_directory():
    return directory


class PlotPatch:
    def __init__(self):
        self.paths = []

    def __call__(self, path, *args, **kwargs):
        self.paths.append(path)


@pytest.fixture(name="plot_patch")
def make_plot_patch(monkeypatch):
    plot_patch = PlotPatch()
    monkeypatch.setattr(pyplot, "savefig", plot_patch)
    return plot_patch


@pytest.fixture(autouse=True, scope="session")
def remove_logs():
    yield
    for d, _, files in os.walk(directory):
        for file in files:
            if file.endswith(".log"):
                os.remove(path.join(d, file))


@pytest.fixture(name="model_gaussian_x1")
def make_model_gaussian_x1():
    return fixtures.make_model_gaussian_x1()


@pytest.fixture(name="samples_x5")
def make_samples_x5():
    return fixtures.make_samples_x5()
