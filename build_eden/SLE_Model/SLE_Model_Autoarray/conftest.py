from os import path
from os.path import dirname
import pytest

from SLE_Model_Autoconf import conf

from SLE_Model_Autofit import fixtures

directory = path.abspath(dirname(__file__))


@pytest.fixture(autouse=True)
def set_config_path(request):

    conf.instance.push(
        new_path=path.join(
            directory, "../SLE_Model_Programs/auxdir/SLE_Model_Programs/config"
        ),
        output_path=path.join(directory, "output"),
    )
