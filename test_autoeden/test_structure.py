import shutil
from pathlib import Path

import pytest

from autoeden import File


@pytest.fixture(
    name="child"
)
def make_child(package):
    return sorted(
        package.children,
        key=str
    )[1]


def test_top_level(package):
    assert package.is_top_level is True
    assert len(package.children) > 1


def test_path(package, child):
    assert package.target_name == "VIS_CTI_Autoeden"
    assert str(package.target_path) == "VIS_CTI/VIS_CTI_Autoeden/python/VIS_CTI_Autoeden"
    assert str(child.target_path) == f"VIS_CTI/VIS_CTI_Autoeden/python/VIS_CTI_Autoeden/{child.target_file_name}"


def test_init(
        package
):
    assert package["__init__"].target_file_name == "__init__.py"


def test_file(package):
    file = File(
        Path(__file__),
        prefix="",
        parent=package
    )

    assert len(file.imports) > 1
    assert len(file.project_imports) == 1


def _test_generate_target_directories(
        output_path
):
    assert output_path.exists()
    assert (
            output_path / "VIS_CTI_Autofit/VIS_CTI_Tools/VIS_CTI_Edenise/VIS_CTI_Structure/VIS_CTI_Item.py"
    )


@pytest.fixture(
    name="output_path"
)
def make_output_path(package):
    output_directory = Path(
        __file__
    ).parent / "output"
    package.generate_target(
        output_directory
    )
    yield output_directory
    shutil.rmtree(output_directory)
