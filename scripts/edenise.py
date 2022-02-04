#!/usr/bin/env python

from configparser import ConfigParser
from sys import argv

from autoeden import Package
from autoeden import edenise


def main(
        root_directory
):
    try:
        config = ConfigParser()
        config.read(
            f"{root_directory}/eden.ini"
        )

        section = config["eden"]

        package = Package.from_config(
            section
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
        argv[1]
    )
