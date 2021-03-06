import importlib
from pathlib import Path

import pytest

from autoeden import Package

package_directory = Path(
    __file__
).parent.parent / "autoeden"


@pytest.fixture(
    name="package"
)
def make_package():
    prefix = "VIS_CTI"
    autoconf = Package(
        Path(
            importlib.import_module(
                "autoconf"
            ).__file__
        ).parent,
        prefix=prefix,
        is_top_level=False,
        should_rename_modules=True,
    )
    autofit = Package(
        Path(
            importlib.import_module(
                "autofit"
            ).__file__
        ).parent,
        prefix=prefix,
        is_top_level=False,
        should_rename_modules=True,
    )
    return Package(
        Path(
            importlib.import_module(
                "autoeden"
            ).__file__
        ).parent,
        prefix="VIS_CTI",
        is_top_level=True,
        eden_dependencies=[autoconf, autofit],
        should_rename_modules=True
    )


@pytest.fixture(
    name="file"
)
def make_file(
        package
):
    return package[
        "__init__"
    ]


directory = Path(
    __file__
).parent


@pytest.fixture(
    name="examples_directory"
)
def make_examples_directory():
    return directory / "examples"


@pytest.fixture(
    name="eden_output_directory"
)
def make_eden_output_directory():
    return directory / "output"
