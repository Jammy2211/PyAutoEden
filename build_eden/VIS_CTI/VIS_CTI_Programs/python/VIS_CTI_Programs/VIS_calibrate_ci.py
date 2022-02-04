"""
@file: python/RemoveCTI/VIS_simulate_ci.py
@author: jnightingale
@date: 03/09/16

History:
2018-02-24 (CG):
    Close files that were not closed
    Suppress in_hdu0 and in_file0 (useless)
"""


import argparse
import ElementsKernel.Logging as log

from SHE_ArCTICPy import traps, ccd
from VIS_CTI_Autoconf import conf
from VIS_CTI_Autocti.VIS_CTI_Util import clocker as clock
from VIS_CTI_Autocti.VIS_CTI_Model import model_util
from VIS_CTI_Autocti import VIS_CTI_ChargeInjection


def calibrate_cti(imaging_ci_list, config_path, output_path):
    """
    @brief The "main" method.
    @details
        This method is the entry point to the program. In this sense, it is
        similar to a main (and it is why it is called mainMethod()).
    """

    logger = log.getLogger("VIS_calibrate_ci")
    logger.info("CTI Calibration starting.")

    conf.instance.push(new_path=config_path, output_path=output_path)

    """
    __Example: Modeling__

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
    clocker = clock.Clocker2D(parallel_express=5, parallel_charge_injection_mode=True)

    """
    __Model__

    We compose our lens model using `Trap` and `CCD` objects, which are what add CTI to our images during clocking and 
    read out. In this example our CTI model is:

     - Two parallel `TrapInstantCapture`'s which capture electrins during clokcing intant in the parallel direction. 
     - A simple `CCD` volume beta parametrization.

    The number of free parameters and therefore the dimensionality of non-linear parameter space is N=12.
    """
    from VIS_CTI_Autofit.VIS_CTI_Mapper.VIS_CTI_PriorModel.prior_model import (
        PriorModel as Model,
    )
    from VIS_CTI_Autofit.VIS_CTI_Mapper.VIS_CTI_PriorModel.collection import (
        CollectionPriorModel as Collection,
    )

    parallel_traps = [Model(traps.TrapInstantCapture)]
    parallel_ccd = Model(ccd.CCDPhase)
    parallel_ccd.well_notch_depth = 0.0
    parallel_ccd.full_well_depth = 84700.0

    model = Collection(
        cti=Model(
            model_util.CTI2D, parallel_traps=parallel_traps, parallel_ccd=parallel_ccd
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
    from VIS_CTI_Autofit.VIS_CTI_NonLinear.VIS_CTI_Nest.VIS_CTI_Dynesty.static import (
        DynestyStatic,
    )

    search = DynestyStatic(name="parallel[x1]", n_live_points=50)

    """
    __Settings__

    To reduce run-times, we trim the `ImagingCI` data from the high resolution data (e.g. 2000 columns) to just 50 columns 
    to speed up the model-fit at the expense of inferring larger errors on the CTI model.
    
    We also mask the FPR of the data during the model-fit.
    """
    mask_ci = VIS_CTI_ChargeInjection.Mask2DCI.unmasked(
        shape_native=imaging_ci_list[0].shape_native,
        pixel_scales=imaging_ci_list[0].pixel_scales,
    )
    mask_ci = VIS_CTI_ChargeInjection.Mask2DCI.masked_front_edges_and_epers_from_layout(
        mask=mask_ci,
        layout=imaging_ci_list[0].layout,
        settings=VIS_CTI_ChargeInjection.SettingsMask2DCI(
            parallel_front_edge_rows=(0, 200)
        ),
        pixel_scales=imaging_ci_list[0].pixel_scales,
    )

    imaging_ci_trimmed_list = [
        imaging_ci.apply_mask(mask=mask_ci) for imaging_ci in imaging_ci_list
    ]

    imaging_ci_trimmed_list = [
        imaging_ci.apply_settings(
            settings=VIS_CTI_ChargeInjection.SettingsImagingCI(parallel_columns=(0, 1))
        )
        for imaging_ci in imaging_ci_trimmed_list
    ]

    """
    __Analysis__

    The `AnalysisImagingCI` object defines the `log_likelihood_function` used by the non-linear search to fit the 
    model to  the `ImagingCI`dataset.
    """
    from VIS_CTI_Autocti.VIS_CTI_ChargeInjection.VIS_CTI_Model import analysis as a

    analysis_list = [
        a.AnalysisImagingCI(dataset_ci=imaging_ci, clocker=clocker)
        for imaging_ci in imaging_ci_trimmed_list
    ]
    analysis = analysis_list[0]
    # analysis = sum(analysis_list)

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
    logger.info(
        f"Density = {result_list[0].max_log_likelihood_instance.cti.parallel_traps[0].density}"
    )
    logger.info("# Exiting VIS_calibrate_ci mainMethod()")
    logger.info("#")
