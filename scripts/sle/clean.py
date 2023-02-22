import glob
import os

eden_prefix = "SLE_Model"
eden_path = f"{os.getcwd()}/../build_eden/{eden_prefix}"

FILES_OMIT = ["conftest.py"]
FOLDERS_OMIT = ["output", "SLE_Model_Programs"]


def main():

    # Removing old .py files from SLE_Model modules.

    os.chdir(eden_path)

    for x in [t[0] for t in os.walk(f"../{eden_prefix}")]:

        path = f"{eden_path}/{x}"

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
