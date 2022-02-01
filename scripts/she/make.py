import glob
import os
import shutil
import json
import fileinput

BUILD_PATH = os.getcwd()

EDEN_PATH = f"{os.getcwd()}/../eden"
SHE_ARCTIC_PATH = f"{os.getcwd()}/../SHE_Arctic"
ARCTIC_PATH = f"{os.getcwd()}/../arctic"

FOLDERS_OMIT = ["SHE_Arctic_Programs"]

from subprocess import call


def cp_dir(source, target):
    call(["cp", "-r", source, target])  # Linux


def clearCache():
    """
    Removes generic `__pycache__` .

    The `__pycache__` files are automatically created by python during the simulation.
    This function removes the genric files on simulation start and simulation end.
    """

    clear_files = [".pytest_cache", ".github", "__pycache__", ".eggs"]

    for root, _, filenames in os.walk(EDEN_PATH):
        if sum([file in root for file in clear_files]):
            shutil.rmtree(root, ignore_errors=False)


def main():

    os.chdir(EDEN_PATH)

    if os.path.exists("arctic"):
        shutil.rmtree("arctic")

    cp_dir(ARCTIC_PATH, EDEN_PATH)

    clearCache()

    # move files from eden to VIS_CTI

    os.chdir(SHE_ARCTIC_PATH)

    for x in [t[0] for t in os.walk("../SHE_Arctic")]:

        she_arctic_path = f"{SHE_ARCTIC_PATH}/{x}"
        os.chdir(she_arctic_path)

        if not sum([folder in she_arctic_path for folder in FOLDERS_OMIT]):

            for f in glob.glob("modules.json"):
                with open(f) as infile:
                    modules = json.load(infile)
                    for module, command in modules.items():
                        if command == "all":
                            file_list = os.listdir(f"{EDEN_PATH}/{module}")
                        elif command == "*.cpp":
                            file_list = os.listdir(f"{EDEN_PATH}/{module}")
                            file_list = [
                                file for file in file_list if file.endswith(".cpp")
                            ]
                        else:
                            file_list = command.strip("][").split(", ")

                        for file in file_list:

                            file_path = f"{EDEN_PATH}/{module}/{file}"

                            if os.path.isdir(file_path):
                                shutil.copytree(
                                    file_path,
                                    f"{she_arctic_path}/{file}",
                                    dirs_exist_ok=True,
                                )
                            else:
                                shutil.copy(file_path, she_arctic_path)

    os.chdir(SHE_ARCTIC_PATH)

    for x in [t[0] for t in os.walk("../SHE_Arctic")]:

        she_arctic_path = f"{SHE_ARCTIC_PATH}/{x}"
        os.chdir(she_arctic_path)

        for f in glob.glob("tests/python/*"):
            if "__init__.py" in f:
                if os.path.isfile(f):
                    os.remove(f)

    os.chdir(EDEN_PATH)

    replace_dict = {
        "arcticpy.src": "SHE_ArCTICPy",
        "arcticpy.": "",
        "import wrapper as w": "import SHE_Arctic_wrapper as w",
    }

    SHE_ARCTIC_PATH_2 = f"{os.getcwd()}/../SHE_Arctic"

    os.chdir(SHE_ARCTIC_PATH_2)

    for x in [t[0] for t in os.walk("../SHE_Arctic")]:

        vis_cti_path = f"{SHE_ARCTIC_PATH_2}/{x}"
        os.chdir(vis_cti_path)

        for f in glob.glob("*.py"):

            for old_text, new_text in replace_dict.items():
                with fileinput.FileInput(f, inplace=True) as file:
                    for line in file:
                        print(line.replace(old_text, new_text), end="")

    os.system(
        f"mv {SHE_ARCTIC_PATH}/SHE_Arctic/src/Cython/wrapper.pyx {SHE_ARCTIC_PATH}/SHE_Arctic/src/Cython/lib/SHE_ArCTIC_wrapper.pyx"
    )

    clearCache()


if __name__ == "__main__":
    main()
