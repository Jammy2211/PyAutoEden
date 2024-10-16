from __future__ import annotations
import logging
import numpy as np
from typing import TYPE_CHECKING, List, Tuple, Union

if TYPE_CHECKING:
    from SLE_Model_Autoarray.SLE_Model_Structures.SLE_Model_Grids.uniform_1d import (
        Grid1D,
    )
    from SLE_Model_Autoarray.SLE_Model_Mask.mask_2d import Mask2D
from SLE_Model_Autoarray import type as ty

logging.basicConfig()
logger = logging.getLogger(__name__)


class Geometry1D:
    def __init__(self, shape_native, pixel_scales, origin=(0.0,)):
        """
        A 1D geometry, representing a uniform rectangular grid of (x) coordinates which has ``shape_native``.

        This class is used for converting coordinates from pixel-units to scaled coordinates via
        the geometry's (x) ``pixel_scales`` conversion factor and its (y,x) ``origin``.

        Parameters
        ----------
        shape_native
            The 1D shape of the array in its ``native`` format (and its 1D mask) whose 1D geometry this object
            represents.
        pixel_scales
            The (x) scaled units to pixel units conversion factors of every pixel. If this is input as a `float`,
            it is converted to a (float,) structure.
        origin
            The (x) scaled units origin of the mask's coordinate system.
        """
        self.shape_native = shape_native
        self.pixel_scales = pixel_scales
        self.origin = origin

    @property
    def shape_slim_scaled(self):
        """
        The (x) 1D slim (and native) shape of the geometry in scaled units.

        This is computed by multiplying the 2D ``shape_native`` (units ``pixels``) with
        the ``pixel_scales`` (units ``scaled/pixels``) conversion factor.
        """
        return (float((self.pixel_scales[0] * self.shape_native[0])),)

    @property
    def scaled_maxima(self):
        """
        The maximum (x) scaled coordinates of the 1D geometry.

        For example, if the geometry's most positive scaled x value is 20.0, this returns (20.0,).
        """
        return (float(((self.shape_slim_scaled[0] / 2.0) + self.origin[0])),)

    @property
    def scaled_minima(self):
        """
        The minimum (x) scaled coordinates of the 1D geometry.

        For example, if the geometry's most negative scaled x value is -20.0, this returns (-20.0,).
        """
        return (((-float((self.shape_slim_scaled[0] / 2.0))) + self.origin[0]),)

    @property
    def extent(self):
        """
        The extent of the geometry in scaled units, returned as a tuple (x_min, x_max).
        """
        return (self.scaled_minima[0], self.scaled_maxima[0])
