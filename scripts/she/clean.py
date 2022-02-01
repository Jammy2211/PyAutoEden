import glob
import os
import shutil

BUILD_PATH = os.getcwd()

EDEN_PATH = f"{os.getcwd()}/../eden"
SHE_ARCTIC_PATH = f"{os.getcwd()}/../SHE_Arctic"

FILES_OMIT = []

FOLDERS_OMIT = ["SHE_Arctic_Programs"]


def main():

    # Removing old .py files from VIS_CTI modules.

    os.chdir(SHE_ARCTIC_PATH)

    for x in [t[0] for t in os.walk("SHE_Arctic")]:

        path = f"{SHE_ARCTIC_PATH}/{x}"

        try:

            os.chdir(path)

            if not sum([folder in path for folder in FOLDERS_OMIT]):
                for f in glob.glob(f"*.pyx"):
                    if not sum([folder in f for folder in FILES_OMIT]):
                        os.remove(f)
                for f in glob.glob(f"*.hpp"):
                    if not sum([folder in f for folder in FILES_OMIT]):
                        os.remove(f)
                for f in glob.glob(f"*.cpp"):
                    if not sum([folder in f for folder in FILES_OMIT]):
                        os.remove(f)

        except FileNotFoundError:

            pass


if __name__ == "__main__":
    main()
