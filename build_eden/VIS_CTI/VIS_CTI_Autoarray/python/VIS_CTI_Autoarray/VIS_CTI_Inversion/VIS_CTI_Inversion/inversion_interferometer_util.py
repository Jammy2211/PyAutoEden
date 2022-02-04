import logging
import numpy as np
from typing import Tuple
from VIS_CTI_Autoarray import numba_util

logger = logging.getLogger(__name__)


@numba_util.jit()
def w_tilde_data_interferometer_from(
    visibilities_real,
    noise_map_real,
    uv_wavelengths,
    grid_radians_slim,
    native_index_for_slim_index,
):
    pass


@numba_util.jit()
def w_tilde_curvature_interferometer_from(
    noise_map_real, uv_wavelengths, grid_radians_slim
):
    """
    The matrix w_tilde is a matrix of dimensions [image_pixels, image_pixels] that encodes the NUFFT of every pair of
    image pixels given the noise map. This can be used to efficiently compute the curvature matrix via the mappings
    between image and source pixels, in a way that omits having to perform the NUFFT on every individual source pixel.
    This provides a significant speed up for inversions of interferometer datasets with large number of visibilities.

    The limitation of this matrix is that the dimensions of [image_pixels, image_pixels] can exceed many 10s of GB's,
    making it impossible to store in memory and its use in linear algebra calculations extremely. The method
    `w_tilde_preload_interferometer_from` describes a compressed representation that overcomes this hurdles. It is
    advised `w_tilde` and this method are only used for testing.

    Parameters
    ----------
    noise_map_real
        The real noise-map values of the interferometer data.
    uv_wavelengths
        The wavelengths of the coordinates in the uv-plane for the interferometer dataset that is to be Fourier
        transformed.
    grid_radians_slim
        The 1D (y,x) grid of coordinates in radians corresponding to real-space mask within which the image that is
        Fourier transformed is computed.

    Returns
    -------
    ndarray
        A matrix that encodes the NUFFT values between the noise map that enables efficient calculation of the curvature
        matrix.
    """
    pass


@numba_util.jit()
def w_tilde_curvature_preload_interferometer_from(
    noise_map_real, uv_wavelengths, shape_masked_pixels_2d, grid_radians_2d
):
    pass


@numba_util.jit()
def w_tilde_curvature_interferometer_via_preload_from(
    w_tilde_preload, native_index_for_slim_index
):
    pass


@numba_util.jit()
def curvature_matrix_via_w_tilde_curvature_preload_interferometer_from(
    curvature_preload,
    pix_indexes_for_sub_slim_index,
    native_index_for_slim_index,
    pixelization_pixels,
):
    pass
