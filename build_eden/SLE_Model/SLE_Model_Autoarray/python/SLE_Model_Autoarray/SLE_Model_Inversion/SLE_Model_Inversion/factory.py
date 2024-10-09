from typing import Dict, List, Optional, Union
from SLE_Model_Autoarray.SLE_Model_Dataset.SLE_Model_Imaging.dataset import Imaging
from SLE_Model_Autoarray.SLE_Model_Dataset.SLE_Model_Interferometer.dataset import (
    Interferometer,
)
from SLE_Model_Autoarray.SLE_Model_Inversion.SLE_Model_Inversion.SLE_Model_Imaging.mapping import (
    InversionImagingMapping,
)
from SLE_Model_Autoarray.SLE_Model_Inversion.SLE_Model_Inversion.SLE_Model_Interferometer.mapping import (
    InversionInterferometerMapping,
)
from SLE_Model_Autoarray.SLE_Model_Inversion.SLE_Model_Inversion.SLE_Model_Interferometer.w_tilde import (
    InversionInterferometerWTilde,
)
from SLE_Model_Autoarray.SLE_Model_Inversion.SLE_Model_Inversion.SLE_Model_Interferometer.lop import (
    InversionInterferometerMappingPyLops,
)
from SLE_Model_Autoarray.SLE_Model_Inversion.SLE_Model_Inversion.dataset_interface import (
    DatasetInterface,
)
from SLE_Model_Autoarray.SLE_Model_Inversion.SLE_Model_LinearObj.linear_obj import (
    LinearObj,
)
from SLE_Model_Autoarray.SLE_Model_Inversion.SLE_Model_LinearObj.func_list import (
    AbstractLinearObjFuncList,
)
from SLE_Model_Autoarray.SLE_Model_Inversion.SLE_Model_Inversion.SLE_Model_Imaging.w_tilde import (
    InversionImagingWTilde,
)
from SLE_Model_Autoarray.SLE_Model_Inversion.SLE_Model_Inversion.settings import (
    SettingsInversion,
)
from SLE_Model_Autoarray.SLE_Model_Structures.SLE_Model_Arrays.uniform_2d import Array2D
from SLE_Model_Autoarray.preloads import Preloads


def inversion_from(
    dataset,
    linear_obj_list,
    settings=SettingsInversion(),
    preloads=Preloads(),
    run_time_dict=None,
):
    """
    Factory which given an input dataset and list of linear objects, creates an `Inversion`.

    An `Inversion` reconstructs the input dataset using a list of linear objects (e.g. a list of analytic functions
    or a pixelized grid). The inversion solves for the values of these linear objects that best reconstruct the
    dataset, via linear matrix algebra.

    Different `Inversion` objects are used for different dataset types (e.g. `Imaging`, `Interferometer`) and
    for different linear algebra formalisms (determined via the input `settings`) which solve for the linear object
    parameters in different ways.

    This factory inspects the type of dataset input and settings of the inversion in order to create the appropriate
    inversion object.

    Parameters
    ----------
    dataset
        The dataset (e.g. `Imaging`, `Interferometer`) whose data is reconstructed via the `Inversion`.
    linear_obj_list
        The list of linear objects (e.g. analytic functions, a mapper with a pixelized grid) which reconstruct the
        input dataset's data and whose values are solved for via the inversion.
    settings
        Settings controlling how an inversion is fitted for example which linear algebra formalism is used.
    preloads
        Preloads in memory certain arrays which may be known beforehand in order to speed up the calculation,
        for example certain matrices used by the linear algebra could be preloaded.
    run_time_dict
        A dictionary which contains timing of certain functions calls which is used for profiling.

    Returns
    -------
    An `Inversion` whose type is determined by the input `dataset` and `settings`.
    """
    if isinstance(dataset.data, Array2D):
        return inversion_imaging_from(
            dataset=dataset,
            linear_obj_list=linear_obj_list,
            settings=settings,
            preloads=preloads,
            run_time_dict=run_time_dict,
        )
    return inversion_interferometer_from(
        dataset=dataset,
        linear_obj_list=linear_obj_list,
        settings=settings,
        run_time_dict=run_time_dict,
    )


def inversion_imaging_from(
    dataset,
    linear_obj_list,
    settings=SettingsInversion(),
    preloads=Preloads(),
    run_time_dict=None,
):
    """
    Factory which given an input `Imaging` dataset and list of linear objects, creates an `InversionImaging`.

    Unlike the `inversion_from` factory this function takes the `data`, `noise_map` and `w_tilde` objects as separate
    inputs, which facilitates certain computations where the `dataset` object is unpacked before the `Inversion` is
    performed (for example if the noise-map is scaled before the inversion to downweight certain regions of the
    data).

    An `Inversion` reconstructs the input dataset using a list of linear objects (e.g. a list of analytic functions
    or a pixelized grid). The inversion solves for the values of these linear objects that best reconstruct the
    dataset, via linear matrix algebra.

    Different `Inversion` objects are used for different linear algebra formalisms (determined via the
    input `settings`) which solve for the linear object parameters in different ways.

    This factory inspects the type of dataset input and settings of the inversion in order to create the appropriate
    inversion object.

    Parameters
    ----------
    dataset
        The dataset (e.g. `Imaging`) whose data is reconstructed via the `Inversion`.
    linear_obj_list
        The list of linear objects (e.g. analytic functions, a mapper with a pixelized grid) which reconstruct the
        input dataset's data and whose values are solved for via the inversion.
    settings
        Settings controlling how an inversion is fitted for example which linear algebra formalism is used.
    preloads
        Preloads in memory certain arrays which may be known beforehand in order to speed up the calculation,
        for example certain matrices used by the linear algebra could be preloaded.
    run_time_dict
        A dictionary which contains timing of certain functions calls which is used for profiling.

    Returns
    -------
    An `Inversion` whose type is determined by the input `dataset` and `settings`.
    """
    if all(
        (
            isinstance(linear_obj, AbstractLinearObjFuncList)
            for linear_obj in linear_obj_list
        )
    ):
        use_w_tilde = False
    elif preloads.use_w_tilde is not None:
        use_w_tilde = preloads.use_w_tilde
    else:
        use_w_tilde = settings.use_w_tilde
    if not settings.use_w_tilde:
        use_w_tilde = False
    if use_w_tilde:
        if preloads.w_tilde is not None:
            w_tilde = preloads.w_tilde
        else:
            w_tilde = dataset.w_tilde
        return InversionImagingWTilde(
            dataset=dataset,
            w_tilde=w_tilde,
            linear_obj_list=linear_obj_list,
            settings=settings,
            preloads=preloads,
            run_time_dict=run_time_dict,
        )
    return InversionImagingMapping(
        dataset=dataset,
        linear_obj_list=linear_obj_list,
        settings=settings,
        preloads=preloads,
        run_time_dict=run_time_dict,
    )


def inversion_interferometer_from(
    dataset,
    linear_obj_list,
    settings=SettingsInversion(),
    preloads=Preloads(),
    run_time_dict=None,
):
    """
    Factory which given an input `Interferometer` dataset and list of linear objects, creates
    an `InversionInterferometer`.

    Unlike the `inversion_from` factory this function takes the `data`, `noise_map` and `w_tilde` objects as separate
    inputs, which facilitates certain computations where the `dataset` object is unpacked before the `Inversion` is
    performed (for example if the noise-map is scaled before the inversion to downweight certain regions of the
    data).

    An `Inversion` reconstructs the input dataset using a list of linear objects (e.g. a list of analytic functions
    or a pixelized grid). The inversion solves for the values of these linear objects that best reconstruct the
    dataset, via linear matrix algebra.

    Different `Inversion` objects are used for different linear algebra formalisms (determined via the
    input `settings`) which solve for the linear object parameters in different ways.

    This factory inspects the type of dataset input and settings of the inversion in order to create the appropriate
    inversion object.

    Parameters
    ----------
    dataset
        The dataset (e.g. `Interferometer`) whose data is reconstructed via the `Inversion`.
    w_tilde
        Object which uses the `Imaging` dataset's PSF / `Convolver` operateor to perform the `Inversion` using the
        w-tilde formalism.
    linear_obj_list
        The list of linear objects (e.g. analytic functions, a mapper with a pixelized grid) which reconstruct the
        input dataset's data and whose values are solved for via the inversion.
    settings
        Settings controlling how an inversion is fitted for example which linear algebra formalism is used.
    preloads
        Preloads in memory certain arrays which may be known beforehand in order to speed up the calculation,
        for example certain matrices used by the linear algebra could be preloaded.
    run_time_dict
        A dictionary which contains timing of certain functions calls which is used for profiling.

    Returns
    -------
    An `Inversion` whose type is determined by the input `dataset` and `settings`.
    """
    try:
        from SLE_Model_Autoarray.SLE_Model_Inversion.SLE_Model_Inversion import (
            inversion_util_secret,
        )
    except ImportError:
        settings.use_w_tilde = False
    if any(
        (
            isinstance(linear_obj, AbstractLinearObjFuncList)
            for linear_obj in linear_obj_list
        )
    ):
        use_w_tilde = False
    else:
        use_w_tilde = settings.use_w_tilde
    if not settings.use_linear_operators:
        if use_w_tilde:
            if preloads.w_tilde is not None:
                w_tilde = preloads.w_tilde
            else:
                w_tilde = dataset.w_tilde
            return InversionInterferometerWTilde(
                dataset=dataset,
                w_tilde=w_tilde,
                linear_obj_list=linear_obj_list,
                settings=settings,
                preloads=preloads,
                run_time_dict=run_time_dict,
            )
        else:
            return InversionInterferometerMapping(
                dataset=dataset,
                linear_obj_list=linear_obj_list,
                settings=settings,
                preloads=preloads,
                run_time_dict=run_time_dict,
            )
    else:
        return InversionInterferometerMappingPyLops(
            dataset=dataset,
            linear_obj_list=linear_obj_list,
            settings=settings,
            preloads=preloads,
            run_time_dict=run_time_dict,
        )
