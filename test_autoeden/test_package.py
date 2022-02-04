from pathlib import Path

import pytest

from autoeden import Package

directory = Path(__file__).parent
autoeden_path = directory.parent / "autoeden"


@pytest.fixture(
    name="package"
)
def make_package():
    return Package.from_config({
        'name': 'autoeden',
        'eden_prefix': 'eden_prefix',
        'eden_dependencies': [{
            "name": "autoeden",
            'eden_prefix': 'dependency_prefix',
        }],
        'should_rename_modules': False,
        'should_remove_type_annotations': False,
    })


def test_parse(package):
    assert package.path == autoeden_path
    assert package.prefix == "eden_prefix"


def test_dependency(package):
    dependency, = package.eden_dependencies
    assert dependency.path == autoeden_path
    assert dependency.prefix == "dependency_prefix"
