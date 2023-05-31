import shutil
from pathlib import Path
import os

from .file import File
from .import_ import Import
from .item import Item
from .line import LineItem
from .package import Package


def edenise(
        root_directory,
        name,
        eden_prefix,
        eden_dependencies,
        target_path=None,
        eden_path=None,
        should_rename_modules=False,
        should_remove_type_annotations=False,
        should_move_config=True,
):
    target_path = target_path or f"{os.getcwd()}/../build_target/{name}_eden"
    eden_path = eden_path or f"{os.getcwd()}/../build_eden/{eden_prefix}"

    print(f"Creating {target_path}...")
    shutil.rmtree(
        target_path,
        ignore_errors=True
    )
    shutil.copytree(
        root_directory,
        target_path,
        symlinks=True
    )

    target_path = Path(target_path)

    package = Package(
        target_path / name,
        prefix=eden_prefix,
        is_top_level=True,
        eden_dependencies=eden_dependencies,
        should_rename_modules=should_rename_modules,
        should_remove_type_annotations=should_remove_type_annotations
    )

    eden_path = Path(eden_path)

    package.generate_target(
        eden_path
    )

    if should_move_config:

        config_path = target_path / name / "config"

        if os.path.exists(config_path):

            shutil.copytree(
                src=target_path / name / "config",
                dst=eden_path / eden_prefix / f"VIS_CTI_{name.capitalize()}"
            )
