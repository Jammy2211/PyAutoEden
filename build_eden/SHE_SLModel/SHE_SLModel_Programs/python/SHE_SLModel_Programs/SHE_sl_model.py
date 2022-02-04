"""
@file: python/RemoveCTI/SHE_sl_model.py
@author: jnightingale
@date: 03/09/16

History:
2018-02-24 (CG):
    Close files that were not closed
    Suppress in_hdu0 and in_file0 (useless)
"""

import numpy as np
from astropy.io import fits
import subprocess
import shutil
import os
import argparse
import ElementsKernel.Logging as log
from ElementsKernel.Auxiliary import getAuxiliaryPath

from SHE_SLModel_Autoconf import conf


def dir_path(string):
    if os.path.isdir(string):
        return string
    else:
        raise NotADirectoryError(string)


def defineSpecificProgramOptions():
    """
    @brief Allows to define the (command line and configuration file) options
    specific to this program
    @details

        See the Elements documentation for more details.
    @return
        An  ArgumentParser.
    """

    parser = argparse.ArgumentParser()

    parser.add_argument("--infile", type=str, help="input image to process")
    parser.add_argument(
        "--outfile", type=str, help="output file name (include .fits extension)"
    )
    parser.add_argument(
        "--configpath",
        type=dir_path,
        help="config path (does not include config folder name)",
    )
    return parser


def mainMethod(args):
    """
    @brief The "main" method.
    @details
        This method is the entry point to the program. In this sense, it is
        similar to a main (and it is why it is called mainMethod()).
    """

    logger = log.getLogger("SHE_sl_model")

    logger.info("#")
    logger.info("# Entering SHE_sl_model mainMethod()")
    logger.info("#")

    in_file = args.infile
    out_file = args.outfile
    config_path = args.configpath

    if config_path is None:
        logger.info(
            "file_layer_entry_point(): No config file name was specified, therefore using default configs in SHE_SLModel_Programs.auxdir"
        )

        config_path = getAuxiliaryPath("SHE_SLModel_Programs")

    conf.instance.push(new_path=config_path)

    logger.info("#")
    logger.info("# Exiting SHE_sl_model mainMethod()")
    logger.info("#")
