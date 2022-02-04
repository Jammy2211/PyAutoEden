#!/usr/bin/env python

from pathlib import Path
from sys import argv

import yaml

from autoeden import Package
from autoeden import edenise


def main(
        root_directory
):
    try:
        with open(root_directory / "eden.yaml") as f:
            config = yaml.safe_load(f)

        package = Package.from_config(
            config
        )

        edenise(
            root_directory=root_directory,
            package=package,
        )
    except ValueError:
        print("Usage: ./edenise.py root_directory")
        exit(1)


if __name__ == "__main__":
    main(
        Path(argv[1])
    )
