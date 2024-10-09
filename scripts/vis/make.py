import glob
import json
import os
import shutil
from autoeden import edenise

from autoeden.util import clearCache, replace_strings, remove_files, move_test_files, black

PYAUTOCONF_PATH = f"{os.getcwd()}/../../../PyAuto/PyAutoConf"
PYAUTOFIT_PATH = f"{os.getcwd()}/../../../PyAuto/PyAutoFit"
PYAUTOARRAY_PATH = f"{os.getcwd()}/../../../PyAuto/PyAutoArray"
PYAUTOCTI_PATH = f"{os.getcwd()}/../../../PyAuto/PyAutoCTI"

eden_prefix = "VIS_CTI"

build_path = f"{os.getcwd()}/../build_eden"
eden_path = f"{build_path}/{eden_prefix}"
tests_path = f"{os.getcwd()}/vis/tests"
manual_path = f"{os.getcwd()}/vis/manual"

def main():

    # Removing old edenised projects.

    os.chdir(f"{os.getcwd()}")

    for f in glob.glob(f"auto*_eden"):
        shutil.rmtree(f)

    with open("vis/replace_dict.json") as json_file:
        replace_dict = json.load(json_file)

    with open("vis/remove_list.json") as json_file:
        remove_list = json.load(json_file)

    edenise(
        root_directory=PYAUTOCONF_PATH,
        name="autoconf",
        eden_prefix=eden_prefix,
        eden_dependencies=None,
        eden_path=build_path,
        should_remove_type_annotations=True,
    )

    edenise(
        root_directory=PYAUTOFIT_PATH,
        name="autofit",
        eden_prefix=eden_prefix,
        eden_dependencies=["autoconf"],
        eden_path=build_path,
        should_remove_type_annotations=True,
    )

    edenise(
        root_directory=PYAUTOARRAY_PATH,
        name="autoarray",
        eden_prefix=eden_prefix,
        eden_dependencies=["autoconf"],
        eden_path=build_path,
        should_remove_type_annotations=True,
    )

    model_path = os.path.join(build_path, "VIS_CTI", "VIS_CTI_Autocti", "python", "VIS_CTI_Autocti", "VIS_CTI_Model")
    shutil.copy(os.path.join(manual_path, "VIS_CTI_Model", "model_util.py"), model_path)

    edenise(
        root_directory=PYAUTOCTI_PATH,
        name="autocti",
        eden_prefix=eden_prefix,
        eden_dependencies=["autoconf", "autofit", "autoarray"],
        eden_path=build_path,
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
