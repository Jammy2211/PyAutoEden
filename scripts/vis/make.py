import glob
import json
import os
import shutil
from autoeden import edenise

from autoeden.util import clearCache, replace_strings, remove_files, black

PYAUTOCONF_PATH = f"{os.getcwd()}/../../PyAutoConf"
PYAUTOFIT_PATH = f"{os.getcwd()}/../../PyAutoFit"
PYAUTOARRAY_PATH = f"{os.getcwd()}/../../PyAutoArray"
PYAUTOCTI_PATH = f"{os.getcwd()}/../../PyAutoCTI"

eden_prefix = "VIS_CTI"

eden_path = f"{os.getcwd()}/../build_eden/{eden_prefix}"

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
        eden_path=eden_path,
        should_remove_type_annotations=True,
    )

    edenise(
        root_directory=PYAUTOFIT_PATH,
        name="autofit",
        eden_prefix=eden_prefix,
        eden_dependencies=["autoconf"],
        eden_path=eden_path,
        should_remove_type_annotations=True,
    )

    edenise(
        root_directory=PYAUTOARRAY_PATH,
        name="autoarray",
        eden_prefix=eden_prefix,
        eden_dependencies=["autoconf"],
        eden_path=eden_path,
        should_remove_type_annotations=True,
    )

    edenise(
        root_directory=PYAUTOCTI_PATH,
        name="autocti",
        eden_prefix=eden_prefix,
        eden_dependencies=["autoconf", "autofit", "autoarray"],
        eden_path=eden_path
    )

    replace_strings(
        eden_path=eden_path,
        eden_prefix=eden_prefix,
        replace_dict=replace_dict,
    )

    remove_files(
        eden_path=eden_path, eden_prefix=eden_prefix, remove_list=remove_list
    )

    black(eden_path=eden_path)
    clearCache(eden_path=eden_path)


if __name__ == "__main__":
    main()
