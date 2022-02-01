import glob
import os
import shutil

BUILD_PATH = os.getcwd()

EDEN_PATH = f"{os.getcwd()}/../eden"
SHE_SLModel_PATH = f"{os.getcwd()}/../SHE_SLModel"

FILES_OMIT = ["conftest.py"]

FOLDERS_OMIT = ["output", "SHE_SLModel_Programs"]


def main():

    # Removing old .py files from SHE_SLModel modules.

    os.chdir(SHE_SLModel_PATH)

    for x in [t[0] for t in os.walk("../SHE_SLModel")]:

        path = f"{SHE_SLModel_PATH}/{x}"

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
