from __future__ import annotations
import logging
import numpy as np
from typing import TYPE_CHECKING, List, Tuple, Union

if TYPE_CHECKING:
    from SLE_Model_Autoarray.SLE_Model_Structures.SLE_Model_Grids.uniform_1d import (
        Grid1D,
    )
    from SLE_Model_Autoarray.SLE_Model_Mask.mask_2d import Mask2D
from SLE_Model_Autoarray.SLE_Model_Mask.abstract_mask import Mask
from SLE_Model_Autoarray.SLE_Model_Mask.SLE_Model_Derive.grid_1d import DeriveGrid1D
from SLE_Model_Autoarray.SLE_Model_Mask.SLE_Model_Derive.mask_1d import DeriveMask1D
from SLE_Model_Autoarray.SLE_Model_Geometry.geometry_1d import Geometry1D
from SLE_Model_Autoarray.SLE_Model_Structures.SLE_Model_Arrays import array_1d_util
from SLE_Model_Autoarray import exc
from SLE_Model_Autoarray import type as ty

logging.basicConfig()
logger = logging.getLogger(__name__)


class Mask1D(Mask):
    def __new__(cls, mask, pixel_scales, sub_size=1, origin=(0.0,), invert=False):
        """
        A 1D mask, representing 1D data on a uniform line of pixels with equal spacing.

        When applied to 1D data it extracts or masks the unmasked image pixels corresponding to mask entries that
        are `False` or 0).

        The mask also defines the geometry of the 1D data structure it is paired to, for example how every pixel
        coordinate on the 1D line of data converts to physical units via the `pixel_scales` and `origin`
        parameters and a sub-grid which is used for performing calculations via super-sampling.

        Parameters
        ----------
        mask
            The ndarray of shape [total_pixels] containing the bool's representing the mask, where `False`
            signifies an entry is unmasked and used in calculations.
        pixel_scales
             The scaled units to pixel units conversion factor of each pixel.
        origin
            The x origin of the mask's coordinate system in scaled units.
        """
        if type(mask) is list:
            mask = np.asarray(mask).astype("bool")
        if invert:
            mask = np.invert(mask)
        if type(pixel_scales) is float:
            pixel_scales = (pixel_scales,)
        if len(mask.shape) != 1:
            raise exc.MaskException("The input mask is not a one dimensional array")
        return Mask.__new__(
            cls=cls,
            mask=mask,
            pixel_scales=pixel_scales,
            sub_size=sub_size,
            origin=origin,
        )

    def __array_finalize__(self, obj):
        super().__array_finalize__(obj=obj)
        if isinstance(obj, Mask1D):
            pass
        else:
            self.origin = (0.0,)

    @property
    def geometry(self):
        """
        Return the 1D geometry of the mask, representing its uniform rectangular grid of (x) coordinates defined by
        its ``shape_native``.
        """
        return Geometry1D(
            shape_native=self.shape_native,
            pixel_scales=self.pixel_scales,
            origin=self.origin,
        )

    @property
    def derive_mask(self):
        return DeriveMask1D(mask=self)

    @property
    def derive_grid(self):
        return DeriveGrid1D(mask=self)

    @classmethod
    def all_false(
        cls, shape_slim, pixel_scales, sub_size=1, origin=(0.0,), invert=False
    ):
        """
        Setup a 1D mask where all pixels are unmasked.

        Parameters
        ----------
        shape_slim
            The (y,x) shape of the mask in units of pixels.
        pixel_scales
            The scaled units to pixel units conversion factor of each pixel.
        """
        return cls(
            mask=np.full(shape=shape_slim, fill_value=False),
            pixel_scales=pixel_scales,
            origin=origin,
            sub_size=sub_size,
            invert=invert,
        )

    @classmethod
    def from_fits(cls, file_path, pixel_scales, sub_size=1, hdu=0, origin=(0.0,)):
        """
        Loads the 1D mask from a .fits file.

        Parameters
        ----------
        file_path
            The full path of the fits file.
        hdu
            The HDU number in the fits file containing the image image.
        pixel_scales
            The scaled units to pixel units conversion factor of each pixel.
        """
        return cls(
            array_1d_util.numpy_array_1d_via_fits_from(file_path=file_path, hdu=hdu),
            pixel_scales=pixel_scales,
            sub_size=sub_size,
            origin=origin,
        )

    @property
    def shape_native(self):
        return self.shape

    @property
    def sub_shape_native(self):
        return ((self.shape[0] * self.sub_size),)

    @property
    def shape_slim(self):
        return self.shape

    def output_to_fits(self, file_path, overwrite=False):
        """
        Write the 1D mask to a .fits file.

        Parameters
        ----------
        file_path
            The full path of the file that is output, including the file name and .fits extension.
        overwrite
            If `True` and a file already exists with the input file_path the .fits file is overwritten. If `False`,
            an error is raised.

        Returns
        -------
        None

        Examples
        --------
        mask = Mask1D(mask=np.full(shape=(5,), fill_value=False))
        mask.output_to_fits(file_path='/path/to/file/filename.fits', overwrite=True)
        """
        array_1d_util.numpy_array_1d_to_fits(
            array_1d=self.astype("float"), file_path=file_path, overwrite=overwrite
        )
