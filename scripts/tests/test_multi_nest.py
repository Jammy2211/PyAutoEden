from VIS_CTI_Autofit.VIS_CTI_Mapper.model_mapper import ModelMapper
from VIS_CTI_Autofit.VIS_CTI_NonLinear.abstract_search import PriorPasser
from VIS_CTI_Autofit.VIS_CTI_NonLinear.VIS_CTI_Nest.multi_nest import MultiNest
import os
from os import path
import shutil
from functools import wraps

import pytest


from VIS_CTI_Autoconf import conf
from VIS_CTI_Autofit.VIS_CTI_Mock import mock

directory = path.dirname(path.realpath(__file__))
pytestmark = pytest.mark.filterwarnings("ignore::FutureWarning")


@pytest.fixture(name="multi_nest_summary_path")
def test_multi_nest_summary():

    multi_nest_summary_path = path.join(
        conf.instance.output_path, "non_linear", "multinest", "summary"
    )

    if path.exists(multi_nest_summary_path):
        shutil.rmtree(multi_nest_summary_path)

    os.mkdir(multi_nest_summary_path)

    return multi_nest_summary_path


@pytest.fixture(name="multi_nest_samples_path")
def test_multi_nest_samples():

    multi_nest_samples_path = path.join(
        conf.instance.output_path, "non_linear", "multinest", "samples"
    )

    if path.exists(multi_nest_samples_path):
        shutil.rmtree(multi_nest_samples_path)

    os.mkdir(multi_nest_samples_path)

    return multi_nest_samples_path


@pytest.fixture(name="multi_nest_resume_path")
def test_multi_nest_resume():

    multi_nest_resume_path = path.join(
        conf.instance.output_path, "non_linear", "multinest", "resume"
    )

    if path.exists(multi_nest_resume_path):
        shutil.rmtree(multi_nest_resume_path)

    os.mkdir(multi_nest_resume_path)

    return multi_nest_resume_path


def create_path(func):
    @wraps(func)
    def wrapper(file_path):
        if not path.exists(file_path):
            os.makedirs(file_path)
        return func(file_path)

    return wrapper


@create_path
def create_summary_4_parameters(file_path):

    summary = open(path.join(file_path, "multinestsummary.txt"), "w")
    summary.write(
        "    0.100000000000000000E+01   -0.200000000000000000E+01    0.300000000000000000E+01"
        "    0.400000000000000000E+01   -0.500000000000000000E+01    0.600000000000000000E+01"
        "    0.700000000000000000E+01    0.800000000000000000E+01"
        "    0.900000000000000000E+01   -1.000000000000000000E+01   -1.100000000000000000E+01"
        "    1.200000000000000000E+01    1.300000000000000000E+01   -1.400000000000000000E+01"
        "   -1.500000000000000000E+01    1.600000000000000000E+01"
        "    0.020000000000000000E+00    0.999999990000000000E+07"
        "    0.020000000000000000E+00    0.999999990000000000E+07\n"
    )
    summary.write(
        "    0.100000000000000000E+01   -0.200000000000000000E+01    0.300000000000000000E+01"
        "    0.400000000000000000E+01   -0.500000000000000000E+01    0.600000000000000000E+01"
        "    0.700000000000000000E+01    0.800000000000000000E+01"
        "    0.900000000000000000E+01   -1.000000000000000000E+01   -1.100000000000000000E+01"
        "    1.200000000000000000E+01    1.300000000000000000E+01   -1.400000000000000000E+01"
        "   -1.500000000000000000E+01    1.600000000000000000E+01"
        "    0.020000000000000000E+00    0.999999990000000000E+07"
    )
    summary.close()


@create_path
def create_weighted_samples_4_parameters(file_path):
    with open(path.join(file_path, "multinest.txt"), "w+") as weighted_samples:
        weighted_samples.write(
            "    0.020000000000000000E+00    0.999999990000000000E+07    0.110000000000000000E+01    "
            "0.210000000000000000E+01    0.310000000000000000E+01    0.410000000000000000E+01\n"
            "    0.020000000000000000E+00    0.999999990000000000E+07    0.090000000000000000E+01    "
            "0.190000000000000000E+01    0.290000000000000000E+01    0.390000000000000000E+01\n"
            "    0.010000000000000000E+00    0.999999990000000000E+07    0.100000000000000000E+01    "
            "0.200000000000000000E+01    0.300000000000000000E+01    0.400000000000000000E+01\n"
            "    0.050000000000000000E+00    0.999999990000000000E+07    0.100000000000000000E+01    "
            "0.200000000000000000E+01    0.300000000000000000E+01    0.400000000000000000E+01\n"
            "    0.100000000000000000E+00    0.999999990000000000E+07    0.100000000000000000E+01    "
            "0.200000000000000000E+01    0.300000000000000000E+01    0.400000000000000000E+01\n"
            "    0.100000000000000000E+00    0.999999990000000000E+07    0.100000000000000000E+01    "
            "0.200000000000000000E+01    0.300000000000000000E+01    0.400000000000000000E+01\n"
            "    0.100000000000000000E+00    0.999999990000000000E+07    0.100000000000000000E+01    "
            "0.200000000000000000E+01    0.300000000000000000E+01    0.400000000000000000E+01\n"
            "    0.100000000000000000E+00    0.999999990000000000E+07    0.100000000000000000E+01    "
            "0.200000000000000000E+01    0.300000000000000000E+01    0.400000000000000000E+01\n"
            "    0.200000000000000000E+00    0.999999990000000000E+07    0.100000000000000000E+01    "
            "0.200000000000000000E+01    0.300000000000000000E+01    0.400000000000000000E+01\n"
            "    0.300000000000000000E+00    0.999999990000000000E+07    0.100000000000000000E+01    "
            "0.200000000000000000E+01    0.300000000000000000E+01    0.400000000000000000E+01"
        )


@create_path
def create_resume(file_path):
    with open(path.join(file_path, "multinestresume.dat"), "w+") as resume:
        resume.write(
            " F\n"
            "        3000       12345           1          50\n"
            "    0.502352236277967168E+05    0.502900436569068333E+05\n"
            " T\n"
            "   0\n"
            " T F     0          50\n"
            "    0.648698272260014622E-26    0.502352236277967168E+05    0.502900436569068333E+05\n"
        )


class TestMulitNest:
    def test__loads_from_config_file_if_not_input(self):
        multi_nest = MultiNest(
            prior_passer=PriorPasser(sigma=2.0, use_errors=False, use_widths=False),
            n_live_points=40,
            sampling_efficiency=0.5,
            const_efficiency_mode=True,
            evidence_tolerance=0.4,
            importance_nested_sampling=False,
            multimodal=False,
            n_iter_before_update=90,
            null_log_evidence=-1.0e80,
            max_modes=50,
            mode_tolerance=-1e88,
            seed=0,
            verbose=True,
            resume=False,
            context=1,
            write_output=False,
            log_zero=-1e90,
            max_iter=1,
            init_MPI=True,
        )

        assert multi_nest.prior_passer.sigma == 2.0
        assert multi_nest.prior_passer.use_errors is False
        assert multi_nest.prior_passer.use_widths is False
        assert multi_nest.config_dict_search["n_live_points"] == 40
        assert multi_nest.config_dict_search["sampling_efficiency"] == 0.5

        multi_nest = MultiNest()

        assert multi_nest.prior_passer.sigma == 3.0
        assert multi_nest.prior_passer.use_errors is True
        assert multi_nest.prior_passer.use_widths is True
        assert multi_nest.config_dict_search["n_live_points"] == 50
        assert multi_nest.config_dict_search["sampling_efficiency"] == 0.2

        model = ModelMapper(mock_class_1=mock.MockClassx4)

        fitness = MultiNest.Fitness(
            analysis=None,
            model=model,
            samples_from_model=multi_nest.samples_from,
            stagger_resampling_likelihood=False,
            paths=None,
        )

        assert fitness.model == model
