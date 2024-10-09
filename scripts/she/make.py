import glob
import os
import shutil
import json
import fileinput
from subprocess import call

from autoeden.util import clearCache, replace_strings, black, build_via_modules, remove_init_files

ARCTIC_PATH = f"{os.getcwd()}/../../../PyAuto/arctic"

target_path = f"{os.getcwd()}/../build_target"

eden_prefix = "SHE_ArCTIC"
store_path = f"{os.getcwd()}/she/store"
template_path = f"{os.getcwd()}/she/template/{eden_prefix}"
eden_path = f"{os.getcwd()}/../build_eden/{eden_prefix}"

print(eden_path)

FOLDERS_OMIT = ["SHE_ArCTIC_Programs"]

def cp_dir(source, target):
    call(["cp", "-r", source, target])  # Linux

def main():

    os.chdir(os.getcwd())

    if os.path.exists(f"{target_path}/arctic"):
        shutil.rmtree(f"{target_path}/arctic")

    if os.path.exists(f"{eden_path}"):
        shutil.rmtree(f"{eden_path}")

    with open("she/replace_dict.json") as json_file:
        replace_dict = json.load(json_file)

    cp_dir(ARCTIC_PATH, target_path)
    cp_dir(store_path, target_path)
    cp_dir(template_path, eden_path)

    build_via_modules(eden_path=eden_path, eden_prefix=eden_prefix, target_path=target_path, FOLDERS_OMIT=FOLDERS_OMIT)

    remove_init_files(eden_path=eden_path, eden_prefix=eden_prefix)

    replace_strings(
        eden_path=eden_path,
        replace_dict=replace_dict,
    )

    os.system(
        f"mv {eden_path}/{eden_prefix}/src/Cython/wrapper.pyx {eden_path}/{eden_prefix}/src/Cython/lib/SHE_ArCTIC_wrapper.pyx"
    )

    black(eden_path=eden_path)
    clearCache(eden_path=eden_path)


if __name__ == "__main__":
    main()
