import glob
import os
import shutil

BUILD_PATH = os.getcwd()

EDEN_PATH = f"{os.getcwd()}/../eden"
VIS_CTI_PATH = f"{os.getcwd()}/../VIS_CTI"

FILES_OMIT = ["conftest.py"]

FOLDERS_OMIT = ["output", "VIS_CTI_Programs"]


def main():

    # Removing old .py files from VIS_CTI modules.

    os.chdir(VIS_CTI_PATH)

    for x in [t[0] for t in os.walk("../VIS_CTI")]:

        path = f"{VIS_CTI_PATH}/{x}"

        try:

            os.chdir(path)

            if not sum([folder in path for folder in FOLDERS_OMIT]):
                for f in glob.glob(f"*.py"):
                    if not sum([folder in f for folder in FILES_OMIT]):
                        os.remove(f)

            for f in glob.glob(f"tests/python/*.py"):
                if not sum([folder in f for folder in FILES_OMIT]):
                    os.remove(f)

        except FileNotFoundError:

            pass


if __name__ == "__main__":
    main()
