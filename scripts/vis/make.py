import glob
import json
import os
import shutil
from autofit.tools.edenise import edenise

from eden_util import clearCache, replace_strings, remove_files, black

BUILD_PATH = os.getcwd()

EDEN_PATH = f"{os.getcwd()}"
VIS_CTI_PATH = f"{os.getcwd()}/.."
PYAUTOCONF_PATH = f"{os.getcwd()}/../PyAutoConf"
PYAUTOFIT_PATH = f"{os.getcwd()}/../PyAutoFit"
PYAUTOARRAY_PATH = f"{os.getcwd()}/../PyAutoArray"
PYAUTOCTI_PATH = f"{os.getcwd()}/../PyAutoCTI"

eden_prefix = "VIS_CTI"


def main():

    # Removing old edenised projects.

    os.chdir(EDEN_PATH)

    for f in glob.glob(f"auto*_eden"):
        shutil.rmtree(f)

    with open("vis/replace_dict.json") as json_file:
        replace_dict = json.load(json_file)

    with open("vis/remove_list.json") as json_file:
        remove_list = json.load(json_file)

    edenise(
        root_directory=PYAUTOCONF_PATH,
        name="autoconf",
        prefix="conf",
        eden_prefix=eden_prefix,
        eden_dependencies=None,
        target_eden_directory=VIS_CTI_PATH,
        should_remove_type_annotations=True,
    )

    edenise(
        root_directory=PYAUTOFIT_PATH,
        name="autofit",
        prefix="fit",
        eden_prefix=eden_prefix,
        eden_dependencies=["autoconf"],
        target_eden_directory=VIS_CTI_PATH,
        should_remove_type_annotations=True,
    )

    edenise(
        root_directory=PYAUTOARRAY_PATH,
        name="autoarray",
        prefix="array",
        eden_prefix=eden_prefix,
        eden_dependencies=["autoconf"],
        target_eden_directory=VIS_CTI_PATH,
        should_remove_type_annotations=True,
    )

    edenise(
        root_directory=PYAUTOCTI_PATH,
        name="autocti",
        prefix="cti",
        eden_prefix=eden_prefix,
        eden_dependencies=["autoconf", "autofit", "autoarray"],
        target_eden_directory=VIS_CTI_PATH,
    )

    replace_strings(eden_prefix=eden_prefix, replace_dict=replace_dict)

    remove_files(eden_prefix=eden_prefix, remove_list=remove_list)

    clearCache(EDEN_PATH=EDEN_PATH)

    black(eden_prefix=eden_prefix)

if __name__ == "__main__":
    main()
