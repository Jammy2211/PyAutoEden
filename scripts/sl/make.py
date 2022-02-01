import glob
import json
import os
import shutil
from autoeden import edenise

from eden_util import clearCache, replace_strings, remove_files, black

BUILD_PATH = os.getcwd()

EDEN_PATH = f"{os.getcwd()}"
SHE_SLMODEL_PATH = f"{os.getcwd()}/.."
PYAUTOGALAXY_PATH = f"{os.getcwd()}/../PyAutoGalaxy"

eden_prefix = "SHE_SLModel"

def main():

    # Removing old edenised projects.

    os.chdir(EDEN_PATH)

    for f in glob.glob(f"auto*_eden"):
        shutil.rmtree(f)

    with open("sl/replace_dict.json") as json_file:
        replace_dict = json.load(json_file)

    with open("sl/remove_list.json") as json_file:
        remove_list = json.load(json_file)

    edenise(
        root_directory=PYAUTOGALAXY_PATH,
        name="autogalaxy",
        prefix="galaxy",
        eden_prefix=eden_prefix,
        eden_dependencies=["autoconf", "autofit", "autoarray"],
        target_eden_directory=SHE_SLMODEL_PATH,
    )

    replace_strings(eden_prefix=eden_prefix, replace_dict=replace_dict)

    remove_files(eden_prefix=eden_prefix, remove_list=remove_list)

    clearCache(EDEN_PATH=EDEN_PATH)

    black(eden_prefix=eden_prefix)


if __name__ == "__main__":
    main()
