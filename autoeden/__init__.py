import os
import shutil
from pathlib import Path

from .file import File
from .import_ import Import
from .item import Item
from .line import LineItem
from .package import Package


from sys import version_info

if version_info >= (3, 10):
    print("Python versions greater than 3.9 not supported")
    exit(1)


def edenise(
    root_directory, package, target_path=None, eden_path=None,
):
    target_path = target_path or f"{os.getcwd()}/../build_target/{package.name}_eden"
    eden_path = eden_path or f"{os.getcwd()}/../build_eden/{package.prefix}"

    print(f"Creating {target_path}...")
    shutil.rmtree(target_path, ignore_errors=True)
    shutil.copytree(root_directory, target_path, symlinks=True)

    eden_path = Path(eden_path)

    package.generate_target(eden_path)
