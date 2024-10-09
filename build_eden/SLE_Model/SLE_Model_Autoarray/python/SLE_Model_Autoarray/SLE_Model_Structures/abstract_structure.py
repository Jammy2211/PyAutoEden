from __future__ import annotations
from abc import ABC
from abc import abstractmethod
from typing import TYPE_CHECKING, Dict, Tuple, Union

if TYPE_CHECKING:
    from SLE_Model_Autoarray.SLE_Model_Structures.SLE_Model_Grids.uniform_1d import (
        Grid1D,
    )
    from SLE_Model_Autoarray.SLE_Model_Structures.SLE_Model_Grids.uniform_2d import (
        Grid2D,
    )
from SLE_Model_Autoarray.abstract_ndarray import AbstractNDArray
from SLE_Model_Autoarray.SLE_Model_Mask.SLE_Model_Derive.grid_2d import DeriveGrid2D
from SLE_Model_Autoarray.SLE_Model_Mask.SLE_Model_Derive.indexes_2d import (
    DeriveIndexes2D,
)
from SLE_Model_Autoarray.SLE_Model_Mask.SLE_Model_Derive.mask_2d import DeriveMask2D
from SLE_Model_Autoarray import exc


class Structure(AbstractNDArray, ABC):
    def __array_finalize__(self, obj):
        if hasattr(obj, "mask"):
            self.mask = obj.mask

    @property
    @abstractmethod
    def slim(self):
        """
        Returns the data structure in its `slim` format which flattens all unmasked values to a 1D array.
        """

    @property
    def geometry(self):
        return self.mask.geometry

    @property
    def derive_grid(self):
        return self.mask.derive_grid

    @property
    def derive_indexes(self):
        return self.mask.derive_indexes

    @property
    def derive_mask(self):
        return self.mask.derive_mask

    @property
    def shape_slim(self):
        return self.mask.shape_slim

    @property
    def shape_native(self):
        return self.mask.shape

    @property
    def pixel_scales(self):
        return self.mask.pixel_scales

    @property
    def pixel_scale(self):
        return self.mask.pixel_scale

    @property
    def pixel_scale_header(self):
        return self.mask.pixel_scale_header

    @property
    def pixel_area(self):
        if len(self.pixel_scales) != 2:
            raise exc.GridException("Cannot compute area of structure which is not 2D.")
        return self.pixel_scales[0] * self.pixel_scales[1]

    @property
    def total_area(self):
        return self.total_pixels * self.pixel_area

    @property
    def origin(self):
        return self.mask.origin

    @property
    def unmasked_grid(self):
        return self.mask.derive_grid.all_false

    @property
    def total_pixels(self):
        return self.shape[0]

    def trimmed_after_convolution_from(self, kernel_shape):
        raise NotImplementedError

    @property
    def hdu_for_output(self):
        raise NotImplementedError
