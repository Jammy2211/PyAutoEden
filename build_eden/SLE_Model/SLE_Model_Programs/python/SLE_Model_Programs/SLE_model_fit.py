"""
@file: python/RemoveCTI/VIS_simulate_ci.py
@author: jnightingale
@date: 03/09/16

History:
2018-02-24 (CG):
    Close files that were not closed
    Suppress in_hdu0 and in_file0 (useless)
"""


import ElementsKernel.Logging as log
import numpy as np

from SLE_Model_Autoconf import conf

import SLE_Model_Autofit as af
import SLE_Model_Autocti as ac


def calibrate_cti(
    imaging_ci_list, config_path, output_fit_path_parallel, output_fit_path_serial
):
    """
    @brief The "main" method.
    @details
        This method is the entry point to the program. In this sense, it is
        similar to a main (and it is why it is called mainMethod()).
    """

    logger = log.getLogger("VIS_calibrate_ci")
    logger.info("Entering VIS_calibrate_ci method")

    """
    __Masking__

    To reduce run-times, we trim the `ImagingCI` data from the high resolution data (e.g. 2000 columns) to just 50 columns 
    to speed up the model-fit at the expense of inferring larger errors on the CTI model.

    We also mask the FPR of the data during the model-fit.
    """
    mask_ci = ac.Mask2D.all_false(
        shape_native=imaging_ci_list[0].shape_native,
        pixel_scales=imaging_ci_list[0].pixel_scales,
    )

    mask_ci = ac.Mask2D.masked_fpr_and_eper_from(
        mask=mask_ci,
        layout=imaging_ci_list[0].layout,
        settings=ac.SettingsMask2D(serial_fpr_pixels=(0, 2048)),
        pixel_scales=imaging_ci_list[0].pixel_scales,
    )

    imaging_ci_masked_list = [
        imaging_ci.apply_mask(mask=mask_ci) for imaging_ci in imaging_ci_list
    ]

    """
    __PARALLEL CTI CALIBRATION__

    First update the output path to a folder named `parallel` which will contain all parallel CTI model fit results.
    """
    conf.instance.push(new_path=config_path, output_path=output_fit_path_parallel)

    """
    To fit a CTI model to a dataset, we must perform CTI modeling, which uses a non-linear search algorithm to fit many
    different CTI models to the dataset.

    Model-fitting is handled by our project **PyAutoFit**, a probablistic programming language for non-linear model
    fitting. The setting up on configuration files is performed by our project **PyAutoConf**. We'll need to import
    both to perform the model-fit.

    In this script, we will fit charge injection imaging which has been subjected to CTI, where:

     - The CTI model consists of two parallel `Trap` species.
     - The `CCD` volume fill parameterization is a simple form with just a *well_fill_beta* parameter.
     - The `CIImaging` is simulated with uniform charge injection lines and no cosmic rays.

    The *Clocker* models the CCD read-out, including CTI. 

    For parallel clocking, we use 'charge injection mode' which transfers the charge of every pixel over the full CCD.
    """
    clocker = ac.Clocker2D(parallel_express=5, parallel_roe=ac.ROEChargeInjection())

    """
    __Model__

    We compose our lens model using `Trap` and `CCD` objects, which are what add CTI to our images during clocking and 
    read out. In this example our CTI model is:

     - Two parallel `TrapInstantCapture`'s which capture electrins during clokcing intant in the parallel direction. 
     - A simple `CCD` volume beta parametrization.

    The number of free parameters and therefore the dimensionality of non-linear parameter space is N=12.
    """
    parallel_trap_list = [af.Model(ac.TrapInstantCapture)]
    parallel_ccd = af.Model(ac.CCDPhase)
    parallel_ccd.well_notch_depth = 0.0
    parallel_ccd.full_well_depth = 200000.0

    model = af.Collection(
        cti=af.Model(
            ac.CTI2D, parallel_trap_list=parallel_trap_list, parallel_ccd=parallel_ccd
        )
    )

    """
    __Search__

    The lens model is fitted to the data using a `NonLinearSearch`. In this example, we use the
    nested sampling algorithm MultiNest with 50 live points.

    The script 'autocti_workspace/examples/model/customize/non_linear_searches.py' gives a description of the types of
    non-linear searches that can be used with **PyAutoCTI**. If you do not know what a non-linear search is or how it 
    operates, checkout chapters 1 and 2 of the HowToCTI lecture series.
    """
    search = af.DynestyStatic(
        name="parallel[x1]", n_live_points=50, vol_dec=0.5, vol_check=2.0
    )

    imaging_ci_trimmed_list = [
        imaging_ci.apply_settings(
            settings=ac.SettingsImagingCI(parallel_pixels=(0, 200))
        )
        for imaging_ci in imaging_ci_masked_list
    ]

    """
    __Analysis__

    The `AnalysisImagingCI` object defines the `log_likelihood_function` used by the non-linear search to fit the 
    model to  the `ImagingCI`dataset.
    """
    analysis_list = [
        ac.AnalysisImagingCI(dataset=imaging_ci, clocker=clocker)
        for imaging_ci in imaging_ci_trimmed_list
    ]

    analysis = sum(analysis_list)

    """
    We can now begin the fit by passing the dataset and mask to the phase, which will use the non-linear search to fit
    the model to the data. 

    The fit outputs visualization on-the-fly, so checkout the path 
    '/path/to/autolens_workspace/output/examples/phase__lens_sie__source_sersic' to see how your fit is doing!
    """
    result_list = search.fit(model=model, analysis=analysis)

    """
    __SERIAL CTI CALIBRATION__

    First update the output path to a folder named `serial` which will contain all serial CTI model fit results.
    """
    conf.instance.push(new_path=config_path, output_path=output_fit_path_serial)

    """
    To fit a CTI model to a dataset, we must perform CTI modeling, which uses a non-linear search algorithm to fit many
    different CTI models to the dataset.

    Model-fitting is handled by our project **PyAutoFit**, a probablistic programming language for non-linear model
    fitting. The setting up on configuration files is performed by our project **PyAutoConf**. We'll need to import
    both to perform the model-fit.

    In this script, we will fit charge injection imaging which has been subjected to CTI, where:

     - The CTI model consists of two parallel `Trap` species.
     - The `CCD` volume fill parameterization is a simple form with just a *well_fill_beta* parameter.
     - The `CIImaging` is simulated with uniform charge injection lines and no cosmic rays.

    The *Clocker* models the CCD read-out, including CTI. 

    For parallel clocking, we use 'charge injection mode' which transfers the charge of every pixel over the full CCD.
    """
    clocker = ac.Clocker2D(serial_express=5)

    """
    __Model__

    We compose our lens model using `Trap` and `CCD` objects, which are what add CTI to our images during clocking and 
    read out. In this example our CTI model is:

     - Two parallel `TrapInstantCapture`'s which capture electrins during clokcing intant in the parallel direction. 
     - A simple `CCD` volume beta parametrization.

    The number of free parameters and therefore the dimensionality of non-linear parameter space is N=12.
    """
    serial_trap_list = [af.Model(ac.TrapInstantCapture)]
    serial_ccd = af.Model(ac.CCDPhase)
    serial_ccd.well_notch_depth = 0.0
    serial_ccd.full_well_depth = 200000.0

    model = af.Collection(
        cti=af.Model(ac.CTI2D, serial_trap_list=serial_trap_list, serial_ccd=serial_ccd)
    )

    """
    __Search__

    The lens model is fitted to the data using a `NonLinearSearch`. In this example, we use the
    nested sampling algorithm MultiNest with 50 live points.

    The script 'autocti_workspace/examples/model/customize/non_linear_searches.py' gives a description of the types of
    non-linear searches that can be used with **PyAutoCTI**. If you do not know what a non-linear search is or how it 
    operates, checkout chapters 1 and 2 of the HowToCTI lecture series.
    """
    search = af.DynestyStatic(
        name="serial[x1]", n_live_points=50, vol_dec=0.5, vol_check=2.0
    )

    imaging_ci_trimmed_list = [
        imaging_ci.apply_settings(settings=ac.SettingsImagingCI(serial_pixels=(10, 50)))
        for imaging_ci in imaging_ci_masked_list
    ]

    """
    __Analysis__

    The `AnalysisImagingCI` object defines the `log_likelihood_function` used by the non-linear search to fit the 
    model to  the `ImagingCI`dataset.
    """
    analysis_list = [
        ac.AnalysisImagingCI(dataset=imaging_ci, clocker=clocker)
        for imaging_ci in imaging_ci_trimmed_list
    ]

    analysis = sum(analysis_list)

    """
    We can now begin the fit by passing the dataset and mask to the phase, which will use the non-linear search to fit
    the model to the data. 

    The fit outputs visualization on-the-fly, so checkout the path 
    '/path/to/autolens_workspace/output/examples/phase__lens_sie__source_sersic' to see how your fit is doing!
    """
    result_list = search.fit(model=model, analysis=analysis)

    """
    Checkout '/path/to/autocti_workspace/examples/model/results.py' for a full description of the result object.
    """
    logger.info("#")
    logger.info("# Exiting VIS_calibrate_ci Method")
    logger.info("#")
