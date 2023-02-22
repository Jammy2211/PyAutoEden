from os import path
from os.path import dirname
import pytest

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
