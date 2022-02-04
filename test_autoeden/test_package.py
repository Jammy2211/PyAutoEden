from pathlib import Path

from autoeden import Package

directory = Path(__file__).parent


def test_parse():
    package = Package.from_config({
        'name': 'autoeden',
        'prefix': 'prefix',
        'eden_prefix': 'eden_prefix',
        'eden_dependencies': 'autoeden',
        'should_rename_modules': "false",
        'should_remove_type_annotations': "false",
    })
    autoeden_path = directory.parent / "autoeden"
    assert package.path == autoeden_path

    dependency, = package.eden_dependencies
    assert dependency.path == autoeden_path
