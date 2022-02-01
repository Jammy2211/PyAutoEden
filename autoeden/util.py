import glob
import json
import os
import shutil
import fileinput
from typing import Dict, List

def clearCache(eden_path):
    """
    Removes generic `__pycache__` files.

    The `__pycache__` files are automatically created by python during the simulation.
    This function removes the genric files on simulation start and simulation end.
    """

    clear_files = [".pytest_cache", ".github", "__pycache__", ".eggs"]

    for root, _, filenames in os.walk(eden_path):
        if sum([file in root for file in clear_files]):
            shutil.rmtree(root, ignore_errors=False)


def replace_strings(eden_path: str, eden_prefix: str, replace_dict: Dict):
    """
    Replace all strings in an edenised project with alternative strings.

    This is used to perform tasks like removing imports of libraries which are not supported by EDEN and updating
    other imports.

    The strings to be replaced are passed as a dictionary, where the keys are the string before replacement and
    values are the string after replacement. This dictionary is loaded from the file `replace.json`.

    Parameters
    ----------
    eden_path
        The path to the eden project, which should be in the `build_eden` folder.
    eden_prefix
        The prefix of the eden project, for example `VIS_CTI` for the project VIS_CTI.
    replace_dict
        The dictionary of strings which are replaced, where keys are the strings searched for in the EDEN project and
        values their replacements.
    """
    os.chdir(eden_path)

    for x in [t[0] for t in os.walk(f"/{eden_prefix}")]:

        pth = f"{eden_path}/{x}"
        os.chdir(pth)

        for f in glob.glob("*.py"):

            for old_text, new_text in replace_dict.items():
                with fileinput.FileInput(f, inplace=True) as file:
                    for line in file:
                        print(line.replace(old_text, new_text), end="")

    os.chdir(eden_path)


def remove_files(eden_path: str, eden_prefix: str, remove_list: List):
    """
    Remove modules and packages in an EDEN project based an input list of strings.

    This is used to remove files which use imports that are not supported by EDEN.

    The names of the modules and packages are passed as a list of strings which is loaded from the file `remove.json`.
    Package names should use the EDENISED name, for example "VIS_CTI_ChargeInjection" instead of "charge_injection".

    Parameters
    ----------
    eden_path
        The path to the eden project, which should be in the `build_eden` folder.
    eden_prefix
        The prefix of the eden project, for example `VIS_CTI` for the project VIS_CTI.
    remove_list
        The list of strings containing the names of the modules and packages that are to be removed.
    """

    for x in [t[0] for t in os.walk(f"{eden_prefix}")]:

        pth = f"{eden_path}/{x}"

        try:

            os.chdir(pth)

            for f in glob.glob("*.py"):

                if f in remove_list:
                    os.remove(f)

                package_name = os.path.split(x)[1]

                if package_name in remove_list:

                    shutil.rmtree(pth)

        except FileNotFoundError:
            pass

    os.chdir(eden_path)


def black(eden_path: str):

    os.chdir(eden_path)
    os.system("black .")

def build_via_modules(eden_path: str, eden_prefix: str, target_path:str, FOLDERS_OMIT: List[str]):
    """
    To build SHE_Arctic, the template project has `module.json` files describing which files are copied from the
    `arctic` package to the SHE_Arctic edenised project.

    This function loads every `module.json` file and uses its replacement dictionary to copy files to the edenised
    project.

    Parameters
    ----------
    eden_path
        The path to the eden project, which should be in the `build_eden` folder.
    eden_prefix
        The prefix of the eden project, for example `VIS_CTI` for the project VIS_CTI.
    eden_path
        The path to the target project, which should be in the `build_target` folder.
    FOLDERS_OMIT
        A list of folders which are omitted from the copying of modules.
    """

    os.chdir(eden_path)

    for x in [t[0] for t in os.walk(f"../{eden_prefix}")]:

        pth = f"{eden_path}/{x}"
        os.chdir(pth)

        if not sum([folder in pth for folder in FOLDERS_OMIT]):

            for f in glob.glob("modules.json"):
                with open(f) as infile:
                    module_dict = json.load(infile)
                    for module, command in module_dict.items():
                        if command == "all":
                            file_list = os.listdir(f"{target_path}/{module}")
                        elif command == "*.cpp":
                            file_list = os.listdir(f"{target_path}/{module}")
                            file_list = [
                                file for file in file_list if file.endswith(".cpp")
                            ]
                        else:
                            file_list = command.strip("][").split(", ")

                        for file in file_list:

                            file_path = f"{target_path}/{module}/{file}"

                            if os.path.isdir(file_path):
                                shutil.copytree(
                                    file_path,
                                    f"{pth}/{file}",
                                    dirs_exist_ok=True,
                                )
                            else:
                                shutil.copy(file_path, pth)

def remove_init_files(eden_path: str, eden_prefix: str):
    """
    Removes the __init__.py files from the test directory of a built EDEN project.

    Parameters
    ----------
    eden_path
        The path to the eden project, which should be in the `build_eden` folder.
    eden_prefix
        The prefix of the eden project, for example `VIS_CTI` for the project VIS_CTI.
    """

    os.chdir(eden_path)

    for x in [t[0] for t in os.walk(f"../{eden_prefix}")]:

        pth = f"{eden_path}/{x}"
        os.chdir(pth)

        for f in glob.glob("tests/python/*"):
            if "__init__.py" in f:
                if os.path.isfile(f):
                    os.remove(f)