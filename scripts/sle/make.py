import glob
import json
import os
import shutil

from autoeden import edenise
from autoeden.util import clearCache, replace_strings, remove_files, move_test_files, black

PYAUTOCONF_PATH = f"{os.getcwd()}/../../PyAutoConf"
PYAUTOFIT_PATH = f"{os.getcwd()}/../../PyAutoFit"
PYAUTOARRAY_PATH = f"{os.getcwd()}/../../PyAutoArray"
PYAUTOGALAXY_PATH = f"{os.getcwd()}/../../PyAutoGalaxy"
PYAUTOLENS_PATH = f"{os.getcwd()}/../../PyAutoLens"

build_path = f"{os.getcwd()}/../build_eden"
eden_prefix = "SLE_Model"
eden_path = f"{os.getcwd()}/../build_eden/{eden_prefix}"
tests_path = f"{os.getcwd()}/sle/tests"
manual_path = f"{os.getcwd()}/sle/manual"

def main():

    # Removing old edenised projects.

    os.chdir(os.getcwd())

    for f in glob.glob(f"auto*_eden"):
        shutil.rmtree(f)

    with open("sle/replace_dict.json") as json_file:
        replace_dict = json.load(json_file)

    with open("sle/remove_list.json") as json_file:
        remove_list = json.load(json_file)

    # edenise(
    #     root_directory=PYAUTOCONF_PATH,
    #     name="autoconf",
    #     eden_prefix=eden_prefix,
    #     eden_dependencies=None,
    #     eden_path=build_path,
    #     should_remove_type_annotations=True,
    # )
    #
    # edenise(
    #     root_directory=PYAUTOFIT_PATH,
    #     name="autofit",
    #     eden_prefix=eden_prefix,
    #     eden_dependencies=["autoconf"],
    #     eden_path=build_path,
    #     should_remove_type_annotations=True,
    # )
    #
    # edenise(
    #     root_directory=PYAUTOARRAY_PATH,
    #     name="autoarray",
    #     eden_prefix=eden_prefix,
    #     eden_dependencies=["autoconf"],
    #     eden_path=build_path,
    #     should_remove_type_annotations=True,
    # )
    #
    # nest_path = os.path.join(build_path, "SLE_Model", "SLE_Model_Autofit", "python", "SLE_Model_Autofit", "SLE_Model_NonLinear", "SLE_Model_Nest")
    #
    # try:
    #     shutil.rmtree(os.path.join(nest_path, "SLE_Model_Dynesty"))
    # except FileNotFoundError:
    #     pass
    #
    # shutil.copytree(os.path.join(manual_path, "SLE_Model_Dynesty"), os.path.join(nest_path, "SLE_Model_Dynesty"))
    #
    # edenise(
    #     root_directory=PYAUTOGALAXY_PATH,
    #     name="autogalaxy",
    #     eden_prefix=eden_prefix,
    #     eden_dependencies=["autoconf", "autofit", "autoarray"],
    #     eden_path=build_path,
    #     should_remove_type_annotations=True,
    # )

    edenise(
        root_directory=PYAUTOLENS_PATH,
        name="autolens",
        eden_prefix=eden_prefix,
        eden_dependencies=["autoconf", "autofit", "autoarray", "autogalaxy"],
        eden_path=build_path,
        should_remove_type_annotations=True,
    )

    replace_strings(
        eden_path=eden_path,
        replace_dict=replace_dict,
    )

    remove_files(
        eden_path=eden_path, remove_list=remove_list
    )

    move_test_files(tests_path=tests_path, eden_path=eden_path)

    black(eden_path=eden_path)
    clearCache(eden_path=eden_path)

if __name__ == "__main__":
    main()
