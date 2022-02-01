import glob
import json
import os
import shutil

from autoeden import edenise
from autoeden.util import clearCache, replace_strings, remove_files, black

PYAUTOGALAXY_PATH = f"{os.getcwd()}/../../PyAutoGalaxy"

eden_prefix = "SHE_SLModel"
eden_path = f"{os.getcwd()}/../build_eden/{eden_prefix}"


def main():

    # Removing old edenised projects.

    os.chdir(os.getcwd())

    for f in glob.glob(f"auto*_eden"):
        shutil.rmtree(f)

    with open("sl/replace_dict.json") as json_file:
        replace_dict = json.load(json_file)

    with open("sl/remove_list.json") as json_file:
        remove_list = json.load(json_file)

    edenise(
        root_directory=PYAUTOGALAXY_PATH,
        name="autogalaxy",
        eden_prefix=eden_prefix,
        eden_dependencies=["autoconf", "autofit", "autoarray"],
        eden_path=eden_path,
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
