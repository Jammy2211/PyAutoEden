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


#
# from VIS_CTI_Autoarray.VIS_CTI_Mock import fixtures
#
#
# @pytest.fixture(name="mask_1d_7")
# def make_mask_1d_7():
#     return fixtures.make_mask_1d_7()
#
#
# @pytest.fixture(name="mask_2d_7x7")
# def make_mask_2d_7x7():
#     return fixtures.make_mask_2d_7x7()
#
#
# @pytest.fixture(name="sub_mask_2d_7x7")
# def make_sub_mask_2d_7x7():
#     return fixtures.make_sub_mask_2d_7x7()
#
#
# @pytest.fixture(name="mask_2d_7x7_1_pix")
# def make_mask_2d_7x7_1_pix():
#     return fixtures.make_mask_2d_7x7_1_pix()
#
#
# @pytest.fixture(name="array_2d_7x7")
# def make_array_2d_7x7():
#     return fixtures.make_array_2d_7x7()
#
#
# @pytest.fixture(name="layout_2d_7x7")
# def make_layout_2d_7x7():
#     return fixtures.make_layout_2d_7x7()
#
#
# @pytest.fixture(name="array_2d_layout_7x7")
# def make_array_2d_layout_7x7():
#     return fixtures.make_array_2d_layout_7x7()
#
#
# @pytest.fixture(name="grid_1d_7")
# def make_grid_1d_7():
#     return fixtures.make_grid_1d_7()
#
#
# @pytest.fixture(name="sub_grid_1d_7")
# def make_sub_grid_1d_7():
#     return fixtures.make_sub_grid_1d_7()
#
#
# @pytest.fixture(name="grid_2d_7x7")
# def make_grid_2d_7x7():
#     return fixtures.make_grid_2d_7x7()
#
#
# @pytest.fixture(name="sub_grid_2d_7x7")
# def make_sub_grid_2d_7x7():
#     return fixtures.make_sub_grid_2d_7x7()
#
#
# @pytest.fixture(name="grid_2d_iterate_7x7")
# def make_grid_2d_iterate_7x7():
#     return fixtures.make_grid_2d_iterate_7x7()
#
#
# @pytest.fixture(name="grid_2d_irregular_7x7")
# def make_grid_2d_irregular_7x7():
#     return fixtures.make_grid_2d_irregular_7x7()
#
#
# @pytest.fixture(name="grid_2d_irregular_7x7_list")
# def make_grid_2d_irregular_7x7_list():
#     return fixtures.make_grid_2d_irregular_7x7_list()
#
#
# @pytest.fixture(name="blurring_grid_2d_7x7")
# def make_blurring_grid_2d_7x7():
#     return fixtures.make_blurring_grid_2d_7x7()
#
#
# @pytest.fixture(name="image_7x7")
# def make_image_7x7():
#     return fixtures.make_image_7x7()
#
#
# @pytest.fixture(name="noise_map_7x7")
# def make_noise_map_7x7():
#     return fixtures.make_noise_map_7x7()
#
#
# @pytest.fixture(name="imaging_7x7")
# def make_imaging_7x7():
#     return fixtures.make_imaging_7x7()
#
#
# @pytest.fixture(name="fit_imaging_7x7")
# def make_imaging_fit_x1_plane_7x7():
#     return fixtures.make_imaging_fit_x1_plane_7x7()
#
#
# @pytest.fixture(name="euclid_data")
# def make_euclid_data():
#     return fixtures.make_euclid_data()
#
#

### Arctic ###

from VIS_CTI_Autocti import fixtures


@pytest.fixture(name="trap_0")
def make_trap_0():
    return fixtures.make_trap_0()


@pytest.fixture(name="trap_1")
def make_trap_1():
    return fixtures.make_trap_1()


@pytest.fixture(name="traps_x1")
def make_traps_x1():
    return fixtures.make_traps_x1()


@pytest.fixture(name="traps_x2")
def make_traps_x2():
    return fixtures.make_traps_x2()


@pytest.fixture(name="ccd")
def make_ccd():
    return fixtures.make_ccd()


@pytest.fixture(name="clocker_1d")
def make_clocker_1d():
    return fixtures.make_clocker_1d()


@pytest.fixture(name="parallel_clocker_2d")
def make_parallel_clocker():
    return fixtures.make_parallel_clocker_2d()


@pytest.fixture(name="serial_clocker_2d")
def make_serial_clocker():
    return fixtures.make_serial_clocker_2d()


### MASK ###


@pytest.fixture(name="mask_1d_7_unmasked")
def make_mask_1d_7_unmasked():
    return fixtures.make_mask_1d_7_unmasked()


@pytest.fixture(name="mask_2d_7x7_unmasked")
def make_mask_2d_7x7_unmasked():
    return fixtures.make_mask_2d_7x7_unmasked()


### LINES ###


@pytest.fixture(name="layout_7")
def make_layout_7():
    return fixtures.make_layout_7()


@pytest.fixture(name="data_7")
def make_data_7():
    return fixtures.make_data_7()


@pytest.fixture(name="noise_map_7")
def make_noise_map_7():
    return fixtures.make_noise_map_7()


@pytest.fixture(name="pre_cti_data_7")
def make_pre_cti_data():
    return fixtures.make_pre_cti_data_7()


@pytest.fixture(name="dataset_line_7")
def make_dataset_line_7():
    return fixtures.make_dataset_line_7()


@pytest.fixture(name="fit_line_7")
def make_fit_line_7():
    return fixtures.make_fit_line_7()


### FRAMES ###


@pytest.fixture(name="image_7x7_native")
def make_image_7x7_native():
    return fixtures.make_image_7x7_native()


@pytest.fixture(name="noise_map_7x7_native")
def make_noise_map_7x7_native():
    return fixtures.make_noise_map_7x7_native()


### IMAGING ###


@pytest.fixture(name="imaging_7x7_frame")
def make_imaging_7x7_frame():
    return fixtures.make_imaging_7x7_frame()


### CHARGE INJECTION FRAMES ###


@pytest.fixture(name="layout_ci_7x7")
def make_layout_ci_7x7():
    return fixtures.make_layout_ci_7x7()


@pytest.fixture(name="ci_image_7x7")
def make_ci_image_7x7():
    return fixtures.make_ci_image_7x7()


@pytest.fixture(name="ci_noise_map_7x7")
def make_ci_noise_map_7x7():
    return fixtures.make_ci_noise_map_7x7()


@pytest.fixture(name="pre_cti_data_7x7")
def make_pre_cti_data_7x7():
    return fixtures.make_pre_cti_data_7x7()


@pytest.fixture(name="ci_cosmic_ray_map_7x7")
def make_ci_cosmic_ray_map_7x7():
    return fixtures.make_ci_cosmic_ray_map_7x7()


@pytest.fixture(name="ci_noise_scaling_map_dict_7x7")
def make_ci_noise_scaling_map_dict_7x7():

    return fixtures.make_ci_noise_scaling_map_dict_7x7()


### CHARGE INJECTION IMAGING ###


@pytest.fixture(name="imaging_ci_7x7")
def make_imaging_ci_7x7():

    return fixtures.make_imaging_ci_7x7()


### CHARGE INJECTION FITS ###


@pytest.fixture(name="hyper_noise_scalar_list")
def make_hyper_noise_scalar_list():
    return fixtures.make_hyper_noise_scalar_list()


@pytest.fixture(name="fit_ci_7x7")
def make_fit_ci_7x7():
    return fixtures.make_fit_ci_7x7()


# ### PHASES ###


@pytest.fixture(name="samples_with_result")
def make_samples_with_result():
    return fixtures.make_samples_with_result()


@pytest.fixture(name="analysis_imaging_ci_7x7")
def make_analysis_imaging_ci_7x7():
    return fixtures.make_analysis_imaging_ci_7x7()


# Datasets


@pytest.fixture(name="euclid_data")
def make_euclid_data():
    return fixtures.make_euclid_data()


@pytest.fixture(name="acs_ccd")
def make_acs_ccd():
    return fixtures.make_acs_ccd()


@pytest.fixture(name="acs_quadrant")
def make_acs_quadrant():
    return fixtures.make_acs_quadrant()
