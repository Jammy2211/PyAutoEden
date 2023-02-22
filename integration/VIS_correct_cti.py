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
import logging
import subprocess
import shutil
import os
import argparse

from VIS_CTI_Autoconf import conf

import VIS_CTI_Autocti as ac


logger = logging.getLogger(
    __name__
)

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
    parser.add_argument(
        "--cti_clocker", help="input CTI clocker configuration JSON file"
    )
    parser.add_argument("--cti_model", help="input CTI model configuration JSON file")
    return parser


def mainMethod(args):
    """
    @brief The "main" method.
    @details
        This method is the entry point to the program. In this sense, it is
        similar to a main (and it is why it is called mainMethod()).
    """

    logger.info("#")
    logger.info("# Entering VIS_correct_cti mainMethod()")
    logger.info("#")

    in_file = args.infile
    out_file = args.outfile
    config_path = args.configpath

    conf.instance.push(new_path=config_path)

    #### Setup the CTI Model and Clocker2D ####

    clocker = ac.Clocker2D.from_json(file_path=args.cti_clocker)
    cti = ac.CTI2D.from_json(file_path=args.cti_model)

    hdulist = fits.open(in_file)
    nhdu = len(hdulist)  ### this will be the number of extensions +1 (the primary)

    for ext in range(1, nhdu):

        ext_header = hdulist[ext].header
        gain = ext_header["gain"]

        ### Convert the image to electrons
        data_electrons = hdulist[ext].data * gain

        ### Setup the image, including its Euclid quadrant quad_geometry (e.g. rotations for CTI in different directions) ###

        image = ac.VIS_CTI_Euclid.Array2DEuclid.from_fits_header(
            array=data_electrons, ext_header=ext_header
        )

        data_cti_corrected = clocker.remove_cti(data=image.native, cti=cti)

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


if __name__ == "__main__":

    class Args:

        def __init__(self, infile, outfile, configpath, cti_clocker, cti_model):

            self.infile = infile
            self.outfile = outfile
            self.configpath = configpath
            self.cti_clocker = cti_clocker
            self.cti_model = cti_model

    infile = os.path.join("integration", "dataset", "science.fits.001")
    outfile = os.path.join("integration", "dataset", "out.fits")
    configpath = os.path.join("build_eden", "VIS_CTI", "VIS_CTI_Programs", "auxdir", "VIS_CTI_Programs")
    cti_clocker = os.path.join("integration", "cti_clocker_v540_arcticpy.json")
    cti_model = os.path.join("integration", "cti_model_v540_BOL_arcticpy.json")

    mainMethod(
        args=Args(
            infile,
            outfile,
            configpath,
            cti_clocker,
            cti_model
        )
    )