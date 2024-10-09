from typing import Dict, List, Optional, Union
from SLE_Model_Autoarray.SLE_Model_Dataset.SLE_Model_Imaging.imaging import Imaging
from SLE_Model_Autoarray.SLE_Model_Dataset.SLE_Model_Imaging.w_tilde import (
    WTildeImaging,
)
from SLE_Model_Autoarray.SLE_Model_Dataset.SLE_Model_Interferometer.w_tilde import (
    WTildeInterferometer,
)
from SLE_Model_Autoarray.SLE_Model_Structures.SLE_Model_Arrays.uniform_2d import Array2D
from SLE_Model_Autoarray.SLE_Model_Structures.visibilities import Visibilities
from SLE_Model_Autoarray.SLE_Model_Structures.visibilities import VisibilitiesNoiseMap
from SLE_Model_Autoarray.SLE_Model_Operators.convolver import Convolver
from SLE_Model_Autoarray.SLE_Model_Operators.transformer import TransformerDFT
from SLE_Model_Autoarray.SLE_Model_Operators.transformer import TransformerNUFFT
from SLE_Model_Autoarray.SLE_Model_Inversion.SLE_Model_LinearObj.linear_obj import (
    LinearObj,
)
from SLE_Model_Autoarray.SLE_Model_Inversion.SLE_Model_LinearObj.func_list import (
    AbstractLinearObjFuncList,
)
from SLE_Model_Autoarray.SLE_Model_Inversion.SLE_Model_Inversion.SLE_Model_Imaging.w_tilde import (
    InversionImagingWTilde,
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
from SLE_Model_Autoarray.SLE_Model_Inversion.SLE_Model_Inversion.settings import (
    SettingsInversion,
)
from SLE_Model_Autoarray.preloads import Preloads


def inversion_from(
    dataset,
    linear_obj_list,
    settings=SettingsInversion(),
    preloads=Preloads(),
    profiling_dict=None,
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
    profiling_dict
        A dictionary which contains timing of certain functions calls which is used for profiling.

    Returns
    -------
    An `Inversion` whose type is determined by the input `dataset` and `settings`.
    """
    if settings.use_w_tilde:
        w_tilde = dataset.w_tilde
    else:
        w_tilde = None
    if isinstance(dataset, Imaging):
        return inversion_imaging_unpacked_from(
            data=dataset.data,
            noise_map=dataset.noise_map,
            convolver=dataset.convolver,
            w_tilde=w_tilde,
            linear_obj_list=linear_obj_list,
            settings=settings,
            preloads=preloads,
            profiling_dict=profiling_dict,
        )
    return inversion_interferometer_unpacked_from(
        data=dataset.visibilities,
        noise_map=dataset.noise_map,
        transformer=dataset.transformer,
        w_tilde=w_tilde,
        linear_obj_list=linear_obj_list,
        settings=settings,
        profiling_dict=profiling_dict,
    )


def inversion_unpacked_from(
    dataset,
    data,
    noise_map,
    w_tilde,
    linear_obj_list,
    settings=SettingsInversion(),
    preloads=Preloads(),
    profiling_dict=None,
):
    """
    Factory which given an input dataset and list of linear objects, creates an `Inversion`.

    Unlike the `inversion_from` factory this function takes the `data`, `noise_map` and `w_tilde` objects as separate
    inputs, which facilitates certain computations where the `dataset` object is unpacked before the `Inversion` is
    performed (for example if the noise-map is scaled before the inversion to downweight certain regions of the
    data).

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
    data
        The data of the dataset (e.g. the `image` of `Imaging` data) which may have been changed.
    noise_map
        The noise_map of the noise_mapset (e.g. the `noise_map` of `Imaging` noise_map) which may have been changed.
    w_tilde
        Object which uses the dataset's operated (e.g. the PSF of `Imaging`) to perform the `Inversion` using the
        w-tilde formalism.
    linear_obj_list
        The list of linear objects (e.g. analytic functions, a mapper with a pixelized grid) which reconstruct the
        input dataset's data and whose values are solved for via the inversion.
    settings
        Settings controlling how an inversion is fitted for example which linear algebra formalism is used.
    preloads
        Preloads in memory certain arrays which may be known beforehand in order to speed up the calculation,
        for example certain matrices used by the linear algebra could be preloaded.
    profiling_dict
        A dictionary which contains timing of certain functions calls which is used for profiling.

    Returns
    -------
    An `Inversion` whose type is determined by the input `dataset` and `settings`.
    """
    if isinstance(dataset, Imaging):
        return inversion_imaging_unpacked_from(
            data=data,
            noise_map=noise_map,
            convolver=dataset.convolver,
            w_tilde=w_tilde,
            linear_obj_list=linear_obj_list,
            settings=settings,
            preloads=preloads,
            profiling_dict=profiling_dict,
        )
    return inversion_interferometer_unpacked_from(
        data=data,
        noise_map=noise_map,
        transformer=dataset.transformer,
        w_tilde=w_tilde,
        linear_obj_list=linear_obj_list,
        settings=settings,
        profiling_dict=profiling_dict,
    )


def inversion_imaging_unpacked_from(
    data,
    noise_map,
    convolver,
    w_tilde,
    linear_obj_list,
    settings=SettingsInversion(),
    preloads=Preloads(),
    profiling_dict=None,
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
    data
        The `image` data of the `Imaging` dataset which may have been changed.
    noise_map
        The noise_map of the `Imaging` dataset which may have been changed.
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
    profiling_dict
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
    if preloads.w_tilde is not None:
        w_tilde = preloads.w_tilde
    if use_w_tilde:
        return InversionImagingWTilde(
            data=data,
            noise_map=noise_map,
            convolver=convolver,
            w_tilde=w_tilde,
            linear_obj_list=linear_obj_list,
            settings=settings,
            preloads=preloads,
            profiling_dict=profiling_dict,
        )
    return InversionImagingMapping(
        data=data,
        noise_map=noise_map,
        convolver=convolver,
        linear_obj_list=linear_obj_list,
        settings=settings,
        preloads=preloads,
        profiling_dict=profiling_dict,
    )


def inversion_interferometer_unpacked_from(
    data,
    noise_map,
    transformer,
    w_tilde,
    linear_obj_list,
    settings=SettingsInversion(),
    preloads=Preloads(),
    profiling_dict=None,
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
    data
        The `image` data of the `Imaging` dataset which may have been changed.
    noise_map
        The noise_map of the `Imaging` dataset which may have been changed.
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
    profiling_dict
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
            return InversionInterferometerWTilde(
                data=data,
                noise_map=noise_map,
                transformer=transformer,
                w_tilde=w_tilde,
                linear_obj_list=linear_obj_list,
                settings=settings,
                preloads=preloads,
                profiling_dict=profiling_dict,
            )
        else:
            return InversionInterferometerMapping(
                data=data,
                noise_map=noise_map,
                transformer=transformer,
                linear_obj_list=linear_obj_list,
                settings=settings,
                preloads=preloads,
                profiling_dict=profiling_dict,
            )
    else:
        return InversionInterferometerMappingPyLops(
            data=data,
            noise_map=noise_map,
            transformer=transformer,
            linear_obj_list=linear_obj_list,
            settings=settings,
            preloads=preloads,
            profiling_dict=profiling_dict,
        )
