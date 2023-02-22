import pytest

from autoeden import File


@pytest.fixture(
    name="file"
)
def make_file(
        package,
        examples_directory
):

    return File(
        examples_directory / "shortcut_imports.py",
        parent=package,
        prefix=""
    )


def test_aliased_relative_import(
        file
):
    assert file.target_string == (
        """
from VIS_CTI_Autofit.VIS_CTI_Mapper.VIS_CTI_PriorModel.prior_model import Model
from VIS_CTI_Autofit.VIS_CTI_Mapper.VIS_CTI_PriorModel.collection import Collection
from VIS_CTI_Autofit.VIS_CTI_Mock.mock import MockSamples
"""
    )
