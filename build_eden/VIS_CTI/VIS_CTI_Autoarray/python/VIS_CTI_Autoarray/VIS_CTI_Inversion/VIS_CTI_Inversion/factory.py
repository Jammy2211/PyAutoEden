from typing import Dict, List, Optional, Union
from VIS_CTI_Autoarray.VIS_CTI_Dataset.imaging import Imaging
from VIS_CTI_Autoarray.VIS_CTI_Structures.VIS_CTI_Arrays.VIS_CTI_TwoD.array_2d import (
    Array2D,
)
from VIS_CTI_Autoarray.VIS_CTI_Structures.visibilities import Visibilities
from VIS_CTI_Autoarray.VIS_CTI_Structures.visibilities import VisibilitiesNoiseMap
from VIS_CTI_Autoarray.VIS_CTI_Operators.convolver import Convolver
from VIS_CTI_Autoarray.VIS_CTI_Operators.transformer import TransformerDFT
from VIS_CTI_Autoarray.VIS_CTI_Operators.transformer import TransformerNUFFT
from VIS_CTI_Autoarray.VIS_CTI_Inversion.linear_obj import LinearObj
from VIS_CTI_Autoarray.VIS_CTI_Inversion.VIS_CTI_LinearEqn.imaging import (
    LEqImagingWTilde,
)
from VIS_CTI_Autoarray.VIS_CTI_Inversion.VIS_CTI_LinearEqn.imaging import (
    LEqImagingMapping,
)
from VIS_CTI_Autoarray.VIS_CTI_Inversion.VIS_CTI_Inversion.matrices import (
    InversionMatrices,
)
from VIS_CTI_Autoarray.VIS_CTI_Inversion.VIS_CTI_Inversion.linear_operator import (
    InversionLinearOperator,
)
from VIS_CTI_Autoarray.VIS_CTI_Inversion.VIS_CTI_LinearEqn.interferometer import (
    LEqInterferometerMapping,
)
from VIS_CTI_Autoarray.VIS_CTI_Inversion.VIS_CTI_LinearEqn.interferometer import (
    LEqInterferometerMappingPyLops,
)
from VIS_CTI_Autoarray.VIS_CTI_Inversion.VIS_CTI_Regularization.abstract import (
    AbstractRegularization,
)
from VIS_CTI_Autoarray.VIS_CTI_Inversion.VIS_CTI_Inversion.settings import (
    SettingsInversion,
)
from VIS_CTI_Autoarray.preloads import Preloads


def inversion_from(
    dataset,
    linear_obj_list,
    regularization_list=None,
    settings=SettingsInversion(),
    preloads=Preloads(),
    profiling_dict=None,
):
    if isinstance(dataset, Imaging):
        return inversion_imaging_unpacked_from(
            image=dataset.image,
            noise_map=dataset.noise_map,
            convolver=dataset.convolver,
            w_tilde=dataset.w_tilde,
            linear_obj_list=linear_obj_list,
            regularization_list=regularization_list,
            settings=settings,
            preloads=preloads,
            profiling_dict=profiling_dict,
        )
    return inversion_interferometer_unpacked_from(
        visibilities=dataset.visibilities,
        noise_map=dataset.noise_map,
        transformer=dataset.transformer,
        linear_obj_list=linear_obj_list,
        regularization_list=regularization_list,
        settings=settings,
        profiling_dict=profiling_dict,
    )


def inversion_imaging_unpacked_from(
    image,
    noise_map,
    convolver,
    w_tilde,
    linear_obj_list,
    regularization_list=None,
    settings=SettingsInversion(),
    preloads=Preloads(),
    profiling_dict=None,
):
    if preloads.use_w_tilde is not None:
        use_w_tilde = preloads.use_w_tilde
    else:
        use_w_tilde = settings.use_w_tilde
    if preloads.w_tilde is not None:
        w_tilde = preloads.w_tilde
    if use_w_tilde:
        leq = LEqImagingWTilde(
            noise_map=noise_map,
            convolver=convolver,
            w_tilde=w_tilde,
            linear_obj_list=linear_obj_list,
            profiling_dict=profiling_dict,
        )
    else:
        leq = LEqImagingMapping(
            noise_map=noise_map,
            convolver=convolver,
            linear_obj_list=linear_obj_list,
            profiling_dict=profiling_dict,
        )
    return InversionMatrices(
        data=image,
        leq=leq,
        regularization_list=regularization_list,
        settings=settings,
        preloads=preloads,
        profiling_dict=profiling_dict,
    )


def inversion_interferometer_unpacked_from(
    visibilities,
    noise_map,
    transformer,
    linear_obj_list,
    regularization_list=None,
    settings=SettingsInversion(),
    preloads=Preloads(),
    profiling_dict=None,
):
    if not settings.use_linear_operators:
        leq = LEqInterferometerMapping(
            noise_map=noise_map,
            transformer=transformer,
            linear_obj_list=linear_obj_list,
            profiling_dict=profiling_dict,
        )
    else:
        leq = LEqInterferometerMappingPyLops(
            noise_map=noise_map,
            transformer=transformer,
            linear_obj_list=linear_obj_list,
            profiling_dict=profiling_dict,
        )
    if not settings.use_linear_operators:
        return InversionMatrices(
            data=visibilities,
            leq=leq,
            regularization_list=regularization_list,
            settings=settings,
            preloads=preloads,
            profiling_dict=profiling_dict,
        )
    return InversionLinearOperator(
        data=visibilities,
        leq=leq,
        regularization_list=regularization_list,
        settings=settings,
        profiling_dict=profiling_dict,
    )
