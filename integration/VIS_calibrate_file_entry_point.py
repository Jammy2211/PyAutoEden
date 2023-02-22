#
# Copyright (C) 2012-2020 Euclid Science Ground Segment
#
# This library is free software; you can redistribute it and/or modify it under the terms of the GNU Lesser General
# Public License as published by the Free Software Foundation; either version 3.0 of the License, or (at your option)
# any later version.
#
# This library is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied
# warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License along with this library; if not, write to
# the Free Software Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA
#

import fitsio
import logging
import numpy as np
from astropy.io import fits

import VIS_CTI_Autofit as af
import VIS_CTI_Autocti as ac

from integration import VIS_calibrate_ci
import os
import json

__all__ = ["file_layer_entry_point"]

log = logging.getLogger(
    __name__
)


def file_layer_entry_point(
    data_input_files, master_input_files, output_path, config_path
):
    """
    This layer handles the I/O to/from files.  It is a wrapper around the algorithm.

    For CTI calibration via charge injection line imaging, the input files are a list of .fits files of all charge
    injection exposures on a per quadrant basis. The list includes all quadrants common to the same CCD as well as
    all charge injection exposures taken on that CCD.

    For example, Euclid's CTI calibration strategy is currently scheduled to take 8 sets of charge injection line
    images (at 8 different charge injection normalizations) over the full FPA every day. The CTI pipeline runner before
    this function is called extracts all 8 images of a quadrant across the 8 charge injection levels. It repeats this
    for all 4 quadrants on a CCD, such that the `input_files` list contains 32 .fits files corresponding to 8 sets of 4
    images that are the charge injection image performed on each quadrant that are common to the same CCD.

    For the pipeline runner, the `output_file` is a .json file which gives strings to all files output by the
    VIS_Calibrate_ci program. This consists of .zip files containing the model-fit results and auxilary data.

    Parameters
    ----------
    data_input_files : array_like of string
        Array of file names of input FITS files.  Each file contains a single quadrant of a single charge injection
        line calibration exposure.
    output_master_fileing
        File name to write the master bias FITS file to.
    """
    log.info(
        f"file_layer_entry_point(): argument 'input_files' are: {data_input_files}"
    )
    log.info(
        f"file_layer_entry_point(): argument 'output_master_file' is: {output_path}"
    )

    if config_path is None:
        log.info(
            "file_layer_entry_point(): No config file name was specified, so CTI calibration cannot be performed"
        )
        return

    if output_path is None:
        log.info(
            "file_layer_entry_point(): No output file name was specified, so CTI calibration cannot be performed"
        )
        return

    log.info(
        "file_layer_entry_point(): Loading, rotating and converting images for CTI calibration..."
    )
    log.info(f"file_layer_entry_point(): Images are: {data_input_files}")

    imaging_ci_list = []

    file_dir = os.path.split(output_path)[0]

    for data_file in data_input_files:

        data_hdulist = fits.open(os.path.join(file_dir, data_file))

        sci_header = data_hdulist[0].header
        data_header = data_hdulist[1].header

        gain = data_header["gain"]
        data_electrons = data_hdulist[1].data * gain

        ccd_id = data_header["CCDID"]
        date_obs = sci_header["DATE"]

        data_header['CI_IJON'] = sci_header['CI_IJON']
        data_header['CI_IJOFF'] = sci_header['CI_IJOFF']
        data_header['CI_VSTAR'] = sci_header['CI_VSTAR']
        data_header['CI_VEND'] = sci_header['CI_VEND']

        image_ci = ac.VIS_CTI_Euclid.Array2DEuclid.from_fits_header(
            array=data_electrons.astype("float"), ext_header=data_header
        )

        layout_ci = ac.Layout2DCI.from_euclid_fits_header(
            ext_header=data_header,
        )

        injection_on = sci_header['CI_IJON']

        injection_norm_list = layout_ci.extract.parallel_fpr.median_list_from(
            array=image_ci, pixels=(injection_on-20, injection_on)
        )

        pre_cti_data = layout_ci.pre_cti_data_non_uniform_from(
            injection_norm_list=injection_norm_list, pixel_scales=image_ci.pixel_scales
        )

        ci_noise_map = ac.Array2D.full(
            fill_value=4.0,
            shape_native=image_ci.shape_native,
            pixel_scales=image_ci.pixel_scales,
        )

        imaging_ci = ac.ImagingCI(
            image=image_ci,
            noise_map=ci_noise_map,
            pre_cti_data=pre_cti_data,
            layout=layout_ci,
        )

        imaging_ci_list.append(imaging_ci)

    output_path += f"{date_obs}_CCD{ccd_id}"

    VIS_calibrate_ci.calibrate_cti(
        imaging_ci_list=imaging_ci_list,
        config_path=config_path,
        output_path=output_path,
    )

    """
    Find all .zip files in the output folder.
    """

    zip_files = {}

    for root, dirs, files in os.walk(output_path):
        for file in files:
            if file.endswith(".zip"):
                zip_files["multinestzip"] = os.path.join(root, file)

    with open(output_path, "w+") as f:
        json.dump(zip_files, f)

    log.info(
        f"file_layer_entry_point(): writing output file point to results of CTI calibration {output_path}"
    )
    log.info("file_layer_entry_point(): end")

if __name__ == "__main__":

    class Args:

        def __init__(self, data_input_files, master_input_files, output_path, config_path):

            self.data_input_files = data_input_files
            self.master_input_files = master_input_files
            self.output_path = output_path
            self.config_path = config_path

#    data_input_files = [os.path.join("integration", "dataset", "ci.fits.001")]
    data_input_files = [os.path.join("integration", "dataset", "cti_broken.fits.041")]
    master_input_files = [None]
    output_path = os.path.join("output")
    config_path = os.path.join("build_eden", "VIS_CTI", "VIS_CTI_Programs", "auxdir", "VIS_CTI_Programs")

    file_layer_entry_point(
        data_input_files,
        master_input_files,
        output_path,
        config_path
    )
