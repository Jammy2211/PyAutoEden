"""
@file: python/RemoveCTI/VIS_correct_cti.py
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

from VIS_CTI_Autoconf import conf
from VIS_CTI_Autocti.VIS_CTI_Util.clocker import Clocker2D

from SHE_ArCTICPy import traps, ccd
from VIS_CTI_Autoarray.VIS_CTI_Instruments import euclid


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

    logger = log.getLogger("VIS_correct_cti")

    logger.info("#")
    logger.info("# Entering VIS_correct_cti mainMethod()")
    logger.info("#")

    in_file = args.infile
    out_file = args.outfile
    config_path = args.configpath

    if config_path is None:
        logger.info(
            "file_layer_entry_point(): No config file name was specified, therefore using default configs in VIS_CTI_Programs.auxdir"
        )

        config_path = getAuxiliaryPath("VIS_CTI_Programs")

    conf.instance.push(new_path=config_path)

    hdulist = fits.open(in_file)
    nhdu = len(hdulist)  ### this will be the number of extensions +1 (the primary)

    for ext in range(1, nhdu):

        ext_header = hdulist[ext].header
        gain = ext_header["gain"]

        ### Convert the image to electrons
        data_electrons = hdulist[ext].data * gain

        ### Setup the image, including its Euclid quadrant quad_geometry (e.g. rotations for CTI in different directions) ###

        image = euclid.Array2DEuclid.from_fits_header(
            array=data_electrons, ext_header=ext_header
        )

        #### Setup the ArcticSettings and Params ####

        parallel_trap_list = [
            traps.TrapInstantCapture(density=0.1656, release_timescale=1.25),
            traps.TrapInstantCapture(density=0.3185, release_timescale=4.4),
        ]
        parallel_ccd = ccd.CCDPhase(
            well_notch_depth=1e-9, well_fill_power=0.58, full_well_depth=200000
        )

        serial_trap_list = [
            traps.TrapInstantCapture(density=0.0442, release_timescale=0.8),
            traps.TrapInstantCapture(density=0.1326, release_timescale=2.5),
            traps.TrapInstantCapture(density=3.9782, release_timescale=20.0),
        ]
        serial_ccd = ccd.CCDPhase(
            well_notch_depth=1e-9, well_fill_power=0.58, full_well_depth=200000
        )

        clocker = Clocker2D(iterations=5, parallel_express=5, serial_express=5)

        data_cti_corrected = clocker.remove_cti(
            data=image,
            parallel_trap_list=parallel_trap_list,
            parallel_ccd=parallel_ccd,
            serial_trap_list=serial_trap_list,
            serial_ccd=serial_ccd,
        )

        data_cti_corrected = data_cti_corrected / gain

        # ext_header = clocker.update_fits_header_info(
        #     ext_header=ext_header,
        #     parallel_trap_list=parallel_trap_list,
        #     parallel_ccd=parallel_ccd,
        #     serial_trap_list=serial_trap_list,
        #     serial_ccd=serial_ccd
        # )

        hdulist[ext].header = ext_header
        hdulist[ext].data = data_cti_corrected.original_orientation.astype(np.float32)

    hdulist.writeto(out_file)
    hdulist.close()

    logger.info("#")
    logger.info("# Exiting VIS_correct_cti mainMethod()")
    logger.info("#")
