from __future__ import annotations
from astropy.io import fits
import copy
import logging
import numpy as np
from pathlib import Path
from typing import TYPE_CHECKING, List, Tuple, Union
from SLE_Model_Autoarray.SLE_Model_Structures.abstract_structure import Structure

if TYPE_CHECKING:
    from SLE_Model_Autoarray.SLE_Model_Structures.SLE_Model_Arrays.uniform_2d import (
        Array2D,
    )
from SLE_Model_Autoconf import cached_property
from SLE_Model_Autoarray.SLE_Model_Mask.abstract_mask import Mask
from SLE_Model_Autoarray import exc
from SLE_Model_Autoarray import type as ty
from SLE_Model_Autoarray.SLE_Model_Geometry.geometry_2d import Geometry2D
from SLE_Model_Autoarray.SLE_Model_Mask.SLE_Model_Derive.mask_2d import DeriveMask2D
from SLE_Model_Autoarray.SLE_Model_Mask.SLE_Model_Derive.grid_2d import DeriveGrid2D
from SLE_Model_Autoarray.SLE_Model_Mask.SLE_Model_Derive.indexes_2d import (
    DeriveIndexes2D,
)
from SLE_Model_Autoarray.SLE_Model_Structures.SLE_Model_Arrays import array_2d_util
from SLE_Model_Autoarray.SLE_Model_Geometry import geometry_util
from SLE_Model_Autoarray.SLE_Model_Structures.SLE_Model_Grids import grid_2d_util
from SLE_Model_Autoarray.SLE_Model_Mask import mask_2d_util

logging.basicConfig()
logger = logging.getLogger(__name__)


class Mask2D(Mask):
    def __init__(
        self, mask, pixel_scales, origin=(0.0, 0.0), invert=False, *args, **kwargs
    ):
        """
        A 2D mask, used for masking values which are associated with a a uniform rectangular grid of pixels.

        When applied to 2D data with the same shape, values in the mask corresponding to ``False`` entries are
        unmasked and therefore used in subsequent calculations. .

        The ``Mask2D`, has in-built functionality which:

        - Maps data structures between two data representations: `slim`` (all unmasked ``False`` values in
          a 1D ``ndarray``) and ``native`` (all unmasked values in a 2D or 3D ``ndarray``).

        - Has a ``Geometry2D`` object (defined by its (y,x) ``pixel scales`` and (y,x) ``origin``)
          which defines how coordinates are converted from pixel units to scaled units.

        - Associates Cartesian ``Grid2D`` objects of (y,x) coordinates with the data structure (e.g.
          a (y,x) grid of all unmasked pixels).

        A detailed description of the 2D mask API is provided below.

        __Slim__

        Below is a visual illustration of a ``Mask2D``, where a total of 10 pixels are unmasked (values are ``False``):

        ::

             x x x x x x x x x x
             x x x x x x x x x x     This is an example ``Mask2D``, where:
             x x x x x x x x x x
             x x x x O O x x x x     x = `True` (Pixel is masked and excluded from the array)
             x x x O O O O x x x     O = `False` (Pixel is not masked and included in the array)
             x x x O O O O x x x
             x x x x x x x x x x
             x x x x x x x x x x
             x x x x x x x x x x
             x x x x x x x x x x

        The mask pixel index's are as follows (the positive / negative direction of the ``Grid2D`` objects associated
        with the mask are also shown on the y and x axes).

        ::

            <--- -ve  x  +ve -->

             x x x x x x x x x x  ^
             x x x x x x x x x x  I
             x x x x x x x x x x  I
             x x x x 0 1 x x x x +ve
             x x x 2 3 4 5 x x x  y
             x x x 6 7 8 9 x x x -ve
             x x x x x x x x x x  I
             x x x x x x x x x x  I
             x x x x x x x x x x \\/
             x x x x x x x x x x

        The ``Mask2D``'s ``slim`` data representation is an ``ndarray`` of shape [total_unmasked_pixels].

        For the ``Mask2D`` above the ``slim`` representation therefore contains 10 entries and two examples of these
        entries are:

        ::

            mask[3] = the 4th unmasked pixel's value.
            mask[6] = the 7th unmasked pixel's value.

        A Cartesian grid of (y,x) coordinates, corresponding to all ``slim`` values (e.g. unmasked pixels) is given
        by:


        __native__

        Masked data represented as an an ``ndarray`` of shape [total_y_values, total_x_values], where all masked
        entries have values of 0.0.

        For the following mask:

        ::

             x x x x x x x x x x
             x x x x x x x x x x     This is an example ``Mask2D``, where:
             x x x x x x x x x x
             x x x x O O x x x x     x = `True` (Pixel is masked and excluded from the array)
             x x x O O O O x x x     O = `False` (Pixel is not masked and included in the array)
             x x x O O O O x x x
             x x x x x x x x x x
             x x x x x x x x x x
             x x x x x x x x x x
             x x x x x x x x x x

        The mask has the following indexes:

        ::

            <--- -ve  x  +ve -->

             x x x x x x x x x x  ^
             x x x x x x x x x x  I
             x x x x x x x x x x  I
             x x x x 0 1 x x x x +ve
             x x x 2 3 4 5 x x x  y
             x x x 6 7 8 9 x x x -ve
             x x x x x x x x x x  I
             x x x x x x x x x x  I
             x x x x x x x x x x  \\/
             x x x x x x x x x x

        In the above array:

        ::

            - mask[0,0] = True (it is masked)
            - mask[0,0] = True (it is masked)
            - mask[3,3] = True (it is masked)
            - mask[3,3] = True (it is masked)
            - mask[3,4] = False (not masked)
            - mask[3,5] = False (not masked)
            - mask[4,5] = False (not masked)

        **SLIM TO NATIVE MAPPING**

        The ``Mask2D`` has functionality which maps data between the ``slim`` and ``native`` data representations.

        For the example mask above, the 1D ``ndarray`` given by ``derive_indexes.slim_to_native`` is:

        ::

            slim_to_native[0] = [3,4]
            slim_to_native[1] = [3,5]
            slim_to_native[2] = [4,3]
            slim_to_native[3] = [4,4]
            slim_to_native[4] = [4,5]
            slim_to_native[5] = [4,6]
            slim_to_native[6] = [5,3]
            slim_to_native[7] = [5,4]
            slim_to_native[8] = [5,5]
            slim_to_native[9] = [5,6]

        Parameters
        ----------
        mask
            The `ndarray` of shape [total_y_pixels, total_x_pixels] containing the `bool`'s representing the
            `mask`, where `False` signifies an entry is unmasked and used in calculations.
        pixel_scales
            The (y,x) scaled units to pixel units conversion factors of every pixel. If this is input as a `float`,
            it is converted to a (float, float) structure.
        origin
            The (y,x) scaled units origin of the mask's coordinate system.
        """
        if type(mask) is list:
            mask = np.asarray(mask).astype("bool")
        if not isinstance(mask, np.ndarray):
            mask = mask._array
        if invert:
            mask = np.invert(mask)
        pixel_scales = geometry_util.convert_pixel_scales_2d(pixel_scales=pixel_scales)
        if len(mask.shape) != 2:
            raise exc.MaskException("The input mask is not a two dimensional array")
        super().__init__(mask=mask, origin=origin, pixel_scales=pixel_scales)

    __no_flatten__ = ("derive_indexes",)

    def __array_finalize__(self, obj):
        super().__array_finalize__(obj=obj)
        if not isinstance(obj, Mask2D):
            self.origin = (0.0, 0.0)

    @property
    def native(self):
        return self

    @property
    def geometry(self):
        """
        Return the 2D geometry of the mask, representing its uniform rectangular grid of (y,x) coordinates defined by
        its ``shape_native``.
        """
        return Geometry2D(
            shape_native=self.shape_native,
            pixel_scales=self.pixel_scales,
            origin=self.origin,
        )

    @property
    def derive_indexes(self):
        return DeriveIndexes2D(mask=self)

    @property
    def derive_mask(self):
        return DeriveMask2D(mask=self)

    @property
    def derive_grid(self):
        return DeriveGrid2D(mask=self)

    @classmethod
    def all_false(cls, shape_native, pixel_scales, origin=(0.0, 0.0), invert=False):
        """
        Create a mask where all pixels are `False` and therefore unmasked.

        Parameters
        ----------
        shape_native
            The 2D shape of the mask that is created.
        pixel_scales
            The (y,x) scaled units to pixel units conversion factors of every pixel. If this is input as a `float`,
            it is converted to a (float, float) structure.
        origin
            The (y,x) scaled units origin of the mask's coordinate system.
        invert
            If `True`, the `bool`'s of the input `mask` are inverted, for example `False`'s become `True`
            and visa versa.
        """
        return cls(
            mask=np.full(shape=shape_native, fill_value=False),
            pixel_scales=pixel_scales,
            origin=origin,
            invert=invert,
        )

    @classmethod
    def circular(
        cls,
        shape_native,
        radius,
        pixel_scales,
        origin=(0.0, 0.0),
        centre=(0.0, 0.0),
        invert=False,
    ):
        """
        Returns a Mask2D (see *Mask2D.__new__*) where all `False` entries are within a circle of input radius.

        The `radius` and `centre` are both input in scaled units.

        Parameters
        ----------
        shape_native
            The (y,x) shape of the mask in units of pixels.
        radius
            The radius in scaled units of the circle within which pixels are `False` and unmasked.
        pixel_scales
            The (y,x) scaled units to pixel units conversion factors of every pixel. If this is input as a `float`,
            it is converted to a (float, float) structure.
        origin
            The (y,x) scaled units origin of the mask's coordinate system.
        centre
            The (y,x) scaled units centre of the circle used to mask pixels.
        invert
            If `True`, the `bool`'s of the input `mask` are inverted, for example `False`'s become `True`
            and visa versa.
        """
        pixel_scales = geometry_util.convert_pixel_scales_2d(pixel_scales=pixel_scales)
        mask = mask_2d_util.mask_2d_circular_from(
            shape_native=shape_native,
            pixel_scales=pixel_scales,
            radius=radius,
            centre=centre,
        )
        return cls(mask=mask, pixel_scales=pixel_scales, origin=origin, invert=invert)

    @classmethod
    def circular_annular(
        cls,
        shape_native,
        inner_radius,
        outer_radius,
        pixel_scales,
        origin=(0.0, 0.0),
        centre=(0.0, 0.0),
        invert=False,
    ):
        """
        Returns a Mask2D (see *Mask2D.__new__*) where all `False` entries are within an annulus of input
        inner radius and outer radius.

        The `inner_radius`, `outer_radius` and `centre` are all input in scaled units.

        Parameters
        ----------
        shape_native
            The (y,x) shape of the mask in units of pixels.
        inner_radius
            The inner radius in scaled units of the annulus within which pixels are `False` and unmasked.
        outer_radius
            The outer radius in scaled units of the annulus within which pixels are `False` and unmasked.
        pixel_scales
            The (y,x) scaled units to pixel units conversion factors of every pixel. If this is input as a `float`,
            it is converted to a (float, float) structure.
        origin
            The (y,x) scaled units origin of the mask's coordinate system.
        centre
            The (y,x) scaled units centre of the annulus used to mask pixels.
        invert
            If `True`, the `bool`'s of the input `mask` are inverted, for example `False`'s become `True`
            and visa versa.
        """
        pixel_scales = geometry_util.convert_pixel_scales_2d(pixel_scales=pixel_scales)
        mask = mask_2d_util.mask_2d_circular_annular_from(
            shape_native=shape_native,
            pixel_scales=pixel_scales,
            inner_radius=inner_radius,
            outer_radius=outer_radius,
            centre=centre,
        )
        return cls(mask=mask, pixel_scales=pixel_scales, origin=origin, invert=invert)

    @classmethod
    def circular_anti_annular(
        cls,
        shape_native,
        inner_radius,
        outer_radius,
        outer_radius_2,
        pixel_scales,
        origin=(0.0, 0.0),
        centre=(0.0, 0.0),
        invert=False,
    ):
        """
        Returns a Mask2D (see *Mask2D.__new__*) where all `False` entries are within an inner circle and second
        outer circle, forming an inverse annulus.

        The `inner_radius`, `outer_radius`, `outer_radius_2` and `centre` are all input in scaled units.

        Parameters
        ----------
        shape_native
            The (y,x) shape of the mask in units of pixels.
        inner_radius
            The inner radius in scaled units of the annulus within which pixels are `False` and unmasked.
        outer_radius
            The first outer radius in scaled units of the annulus within which pixels are `True` and masked.
        outer_radius_2
            The second outer radius in scaled units of the annulus within which pixels are `False` and unmasked and
            outside of which all entries are `True` and masked.
        pixel_scales
            The (y,x) scaled units to pixel units conversion factors of every pixel. If this is input as a `float`,
            it is converted to a (float, float) structure.
        origin
            The (y,x) scaled units origin of the mask's coordinate system.
        centre
            The (y,x) scaled units centre of the anti-annulus used to mask pixels.
        invert
            If `True`, the `bool`'s of the input `mask` are inverted, for example `False`'s become `True`
            and visa versa.
        """
        pixel_scales = geometry_util.convert_pixel_scales_2d(pixel_scales=pixel_scales)
        mask = mask_2d_util.mask_2d_circular_anti_annular_from(
            shape_native=shape_native,
            pixel_scales=pixel_scales,
            inner_radius=inner_radius,
            outer_radius=outer_radius,
            outer_radius_2_scaled=outer_radius_2,
            centre=centre,
        )
        return cls(mask=mask, pixel_scales=pixel_scales, origin=origin, invert=invert)

    @classmethod
    def elliptical(
        cls,
        shape_native,
        major_axis_radius,
        axis_ratio,
        angle,
        pixel_scales,
        origin=(0.0, 0.0),
        centre=(0.0, 0.0),
        invert=False,
    ):
        """
        Returns a Mask2D (see *Mask2D.__new__*) where all `False` entries are within an ellipse.

        The `major_axis_radius`, and `centre` are all input in scaled units.

        Parameters
        ----------
        shape_native
            The (y,x) shape of the mask in units of pixels.
        major_axis_radius
            The major-axis in scaled units of the ellipse within which pixels are unmasked.
        axis_ratio
            The axis-ratio of the ellipse within which pixels are unmasked.
        angle
            The rotation angle of the ellipse within which pixels are unmasked, (counter-clockwise from the positive
             x-axis).
        pixel_scales
            The (y,x) scaled units to pixel units conversion factors of every pixel. If this is input as a `float`,
            it is converted to a (float, float) structure.
        origin
            The (y,x) scaled units origin of the mask's coordinate system.
        centre
            The (y,x) scaled units centred of the ellipse used to mask pixels.
        invert
            If `True`, the `bool`'s of the input `mask` are inverted, for example `False`'s become `True`
            and visa versa.
        """
        pixel_scales = geometry_util.convert_pixel_scales_2d(pixel_scales=pixel_scales)
        mask = mask_2d_util.mask_2d_elliptical_from(
            shape_native=shape_native,
            pixel_scales=pixel_scales,
            major_axis_radius=major_axis_radius,
            axis_ratio=axis_ratio,
            angle=angle,
            centre=centre,
        )
        return cls(mask=mask, pixel_scales=pixel_scales, origin=origin, invert=invert)

    @classmethod
    def elliptical_annular(
        cls,
        shape_native,
        inner_major_axis_radius,
        inner_axis_ratio,
        inner_phi,
        outer_major_axis_radius,
        outer_axis_ratio,
        outer_phi,
        pixel_scales,
        origin=(0.0, 0.0),
        centre=(0.0, 0.0),
        invert=False,
    ):
        """
        Returns a Mask2D (see *Mask2D.__new__*) where all `False` entries are within an elliptical annulus of input
        inner and outer scaled major-axis and centre.

        The `outer_major_axis_radius`, `inner_major_axis_radius` and `centre` are all input in scaled units.

        Parameters
        ----------
        shape_native (int, int)
            The (y,x) shape of the mask in units of pixels.
        pixel_scales
            The scaled units to pixel units conversion factor of each pixel.
        inner_major_axis_radius
            The major-axis in scaled units of the inner ellipse within which pixels are masked.
        inner_axis_ratio
            The axis-ratio of the inner ellipse within which pixels are masked.
        inner_phi
            The rotation angle of the inner ellipse within which pixels are masked, (counter-clockwise from the
            positive x-axis).
        outer_major_axis_radius
            The major-axis in scaled units of the outer ellipse within which pixels are unmasked.
        outer_axis_ratio
            The axis-ratio of the outer ellipse within which pixels are unmasked.
        outer_phi
            The rotation angle of the outer ellipse within which pixels are unmasked, (counter-clockwise from the
            positive x-axis).
        origin
            The (y,x) scaled units origin of the mask's coordinate system.
        centre
            The (y,x) scaled units centre of the elliptical annuli used to mask pixels.
        invert
            If `True`, the `bool`'s of the input `mask` are inverted, for example `False`'s become `True`
            and visa versa.
        """
        pixel_scales = geometry_util.convert_pixel_scales_2d(pixel_scales=pixel_scales)
        mask = mask_2d_util.mask_2d_elliptical_annular_from(
            shape_native=shape_native,
            pixel_scales=pixel_scales,
            inner_major_axis_radius=inner_major_axis_radius,
            inner_axis_ratio=inner_axis_ratio,
            inner_phi=inner_phi,
            outer_major_axis_radius=outer_major_axis_radius,
            outer_axis_ratio=outer_axis_ratio,
            outer_phi=outer_phi,
            centre=centre,
        )
        return cls(mask=mask, pixel_scales=pixel_scales, origin=origin, invert=invert)

    @classmethod
    def from_pixel_coordinates(
        cls,
        shape_native,
        pixel_coordinates,
        pixel_scales,
        origin=(0.0, 0.0),
        buffer=0,
        invert=False,
    ):
        """
        Returns a Mask2D (see *Mask2D.__new__*) where all `False` entries are defined from an input list of list of
        pixel coordinates.

        These may be buffed via an input `buffer`, whereby all entries in all 8 neighboring directions by this
        amount.

        Parameters
        ----------
        shape_native (int, int)
            The (y,x) shape of the mask in units of pixels.
        pixel_coordinates : [[int, int]]
            The input lists of 2D pixel coordinates where `False` entries are created.
        pixel_scales
            The scaled units to pixel units conversion factor of each pixel.
        origin
            The (y,x) scaled units origin of the mask's coordinate system.
        buffer
            All input `pixel_coordinates` are buffed with `False` entries in all 8 neighboring directions by this
            amount.
        invert
            If `True`, the `bool`'s of the input `mask` are inverted, for example `False`'s become `True`
            and visa versa.
        """
        mask = mask_2d_util.mask_2d_via_pixel_coordinates_from(
            shape_native=shape_native,
            pixel_coordinates=pixel_coordinates,
            buffer=buffer,
        )
        return cls(mask=mask, pixel_scales=pixel_scales, origin=origin, invert=invert)

    @classmethod
    def from_fits(
        cls,
        file_path,
        pixel_scales,
        hdu=0,
        origin=(0.0, 0.0),
        resized_mask_shape=None,
        invert=False,
    ):
        """
        Loads the image from a .fits file.

        Parameters
        ----------
        file_path
            The full path of the fits file.
        hdu
            The HDU number in the fits file containing the image image.
        pixel_scales or (float, float)
            The scaled units to pixel units conversion factor of each pixel.
        origin
            The (y,x) scaled units origin of the mask's coordinate system.
        """
        pixel_scales = geometry_util.convert_pixel_scales_2d(pixel_scales=pixel_scales)
        mask = array_2d_util.numpy_array_2d_via_fits_from(file_path=file_path, hdu=hdu)
        if invert:
            mask = np.invert(mask.astype("bool"))
        mask = Mask2D(mask=mask, pixel_scales=pixel_scales, origin=origin)
        if resized_mask_shape is not None:
            mask = mask.resized_from(new_shape=resized_mask_shape)
        return mask

    @classmethod
    def from_primary_hdu(cls, primary_hdu, origin=(0.0, 0.0)):
        """
        Returns an ``Mask2D`` by from a `PrimaryHDU` object which has been loaded via `astropy.fits`

        This assumes that the `header` of the `PrimaryHDU` contains an entry named `PIXSCALE` which gives the
        pixel-scale of the array.

        For a full description of ``Mask2D`` objects, including a description of the ``slim`` and ``native`` attribute
        used by the API, see
        the :meth:`Mask2D class API documentation <autoarray.structures.arrays.uniform_2d.AbstractMask2D.__new__>`.

        Parameters
        ----------
        primary_hdu
            The `PrimaryHDU` object which has already been loaded from a .fits file via `astropy.fits` and contains
            the array data and the pixel-scale in the header with an entry named `PIXSCALE`.
        origin
            The (y,x) scaled units origin of the coordinate system.

        Examples
        --------

        .. code-block:: python

            from astropy.io import fits
            import autoarray as aa

            primary_hdu = fits.open("path/to/file.fits")

            array_2d = aa.Mask2D.from_primary_hdu(
                primary_hdu=primary_hdu,
            )
        """
        return cls(
            mask=cls.flip_hdu_for_ds9(primary_hdu.data.astype("float")),
            pixel_scales=primary_hdu.header["PIXSCALE"],
            origin=origin,
        )

    @property
    def shape_native(self):
        return self.shape

    def trimmed_array_from(self, padded_array, image_shape):
        """
        Map a padded 1D array of values to its original 2D array, trimming all edge values.

        Parameters
        ----------
        padded_array
            A 1D array of values which were computed using a padded grid
        """
        from SLE_Model_Autoarray.SLE_Model_Structures.SLE_Model_Arrays.uniform_2d import (
            Array2D,
        )

        pad_size_0 = self.shape[0] - image_shape[0]
        pad_size_1 = self.shape[1] - image_shape[1]
        trimmed_array = padded_array.native[
            (pad_size_0 // 2) : (self.shape[0] - (pad_size_0 // 2)),
            (pad_size_1 // 2) : (self.shape[1] - (pad_size_1 // 2)),
        ]
        return Array2D.no_mask(
            values=trimmed_array, pixel_scales=self.pixel_scales, origin=self.origin
        )

    def unmasked_blurred_array_from(self, padded_array, psf, image_shape):
        """
        For a padded grid and psf, compute an unmasked blurred image from an unmasked unblurred image.

        This relies on using the lens dataset's padded-grid, which is a grid of (y,x) coordinates which extends over
        the entire image as opposed to just the masked region.

        Parameters
        ----------
        psf : aa.Kernel2D
            The PSF of the image used for convolution.
        unmasked_image_1d
            The 1D unmasked image which is blurred.
        """
        blurred_image = psf.convolved_array_from(array=padded_array)
        return self.trimmed_array_from(
            padded_array=blurred_image, image_shape=image_shape
        )

    @property
    def hdu_for_output(self):
        """
        The mask as a HDU object, which can be output to a .fits file.

        The header of the HDU is used to store the `pixel_scale` of the array, which is used by the `Array2D.from_hdu`.

        This method is used in other projects (E.g. PyAutoGalaxy, PyAutoLens) to conveniently output the array to .fits
        files.

        Returns
        -------
        The HDU containing the data and its header which can then be written to .fits.
        """
        return array_2d_util.hdu_for_output_from(
            array_2d=self.astype("float"), header_dict=self.pixel_scale_header
        )

    def output_to_fits(self, file_path, overwrite=False):
        """
        Write the 2D Mask to a .fits file.

        Before outputting a NumPy array, the array may be flipped upside-down using np.flipud depending on the project
        config files. This is for Astronomy projects so that structures appear the same orientation as `.fits` files
        loaded in DS9.

        Parameters
        ----------
        file_path
            The full path of the file that is output, including the file name and `.fits` extension.
        overwrite
            If `True` and a file already exists with the input file_path the .fits file is overwritten. If `False`, an
            error is raised.

        Returns
        -------
        None

        Examples
        --------
        mask = Mask2D(mask=np.full(shape=(5,5), fill_value=False))
        mask.output_to_fits(file_path='/path/to/file/filename.fits', overwrite=True)
        """
        array_2d_util.numpy_array_2d_to_fits(
            array_2d=self.astype("float"),
            file_path=file_path,
            overwrite=overwrite,
            header_dict=self.pixel_scale_header,
        )

    @property
    def mask_centre(self):
        grid = grid_2d_util.grid_2d_slim_via_mask_from(
            mask_2d=np.array(self), pixel_scales=self.pixel_scales, origin=self.origin
        )
        return grid_2d_util.grid_2d_centre_from(grid_2d_slim=grid)

    @property
    def shape_native_masked_pixels(self):
        """
        The (y,x) shape corresponding to the extent of unmasked pixels that go vertically and horizontally across the
        mask.

        For example, if a mask is primarily surrounded by True entries, and there are 15 False entries going vertically
        and 12 False entries going horizontally in the central regions of the mask, then shape_masked_pixels=(15,12).
        """
        where = np.array(np.where(np.invert(self.astype("bool"))))
        (y0, x0) = np.amin(where, axis=1)
        (y1, x1) = np.amax(where, axis=1)
        return (((y1 - y0) + 1), ((x1 - x0) + 1))

    def rescaled_from(self, rescale_factor):
        """
        Returns the ``Mask2D`` rescaled to a bigger or small shape via input ``rescale_factor``.

        For example, for a ``rescale_factor=2.0`` the following mask:

        ::
           [[ True,  True],
            [False, False]]

        Will double in size and become:

        ::
            [[True,   True,  True,  True],
             [True,   True,  True,  True],
             [False, False, False, False],
             [False, False, False, False]]

        Parameters
        ----------
        rescale_factor
            The factor by which the ``Mask2D`` is rescaled (less than 1.0 produces a smaller mask, greater than 1.0
            produces a bigger mask).

        Examples
        --------

        .. code-block:: python

            import autoarray as aa

            mask_2d = aa.Mask2D(
                mask=[
                     [ True,  True],
                     [False, False]
                ],
                pixel_scales=1.0,
            )

            print(mask_2d.rescaled_from(rescale_factor=2.0)
        """
        from SLE_Model_Autoarray.SLE_Model_Mask.mask_2d import Mask2D

        rescaled_mask = mask_2d_util.rescaled_mask_2d_from(
            mask_2d=np.array(self), rescale_factor=rescale_factor
        )
        return Mask2D(
            mask=rescaled_mask, pixel_scales=self.pixel_scales, origin=self.origin
        )

    def resized_from(self, new_shape, pad_value=0.0):
        """
        Returns the ``Mask2D`` resized to a small or bigger ``ndarraay``, but with the same distribution of
         ``False`` and ``True`` entries.

        Resizing which increases the ``Mask2D`` shape pads it with values on its edge.

        Resizing which reduces the ``Mask2D`` shape removes entries on its edge.

        For example, for a ``new_shape=(4,4)`` the following mask:

        ::
           [[ True,  True],
            [False, False]]

        Will be padded with zeros (``False`` values) and become:

        ::
          [[True,  True,  True, True]
           [True,  True,  True, True],
           [True, False, False, True],
           [True,  True,  True, True]]

        Parameters
        ----------
        new_shape
            The new two-dimensional shape of the resized ``Mask2D``.
        pad_value
            The value new values are padded using if the resized ``Mask2D`` is bigger.

        Examples
        --------

        .. code-block:: python

            import autoarray as aa

            mask_2d = aa.Mask2D(
                mask=[
                     [ True,  True],
                     [False, False]
                ],
                pixel_scales=1.0,
            )

            print(mask_2d.resized_from(new_shape=(4,4))
        """
        resized_mask = array_2d_util.resized_array_2d_from(
            array_2d=np.array(self), resized_shape=new_shape, pad_value=pad_value
        ).astype("bool")
        return Mask2D(
            mask=resized_mask, pixel_scales=self.pixel_scales, origin=self.origin
        )

    @property
    def zoom_centre(self):
        from SLE_Model_Autoarray.SLE_Model_Structures.SLE_Model_Grids.uniform_2d import (
            Grid2D,
        )

        grid = grid_2d_util.grid_2d_slim_via_mask_from(
            mask_2d=np.array(self), pixel_scales=self.pixel_scales, origin=self.origin
        )
        grid = Grid2D(values=grid, mask=self)
        extraction_grid_1d = self.geometry.grid_pixels_2d_from(grid_scaled_2d=grid)
        y_pixels_max = np.max(extraction_grid_1d[:, 0])
        y_pixels_min = np.min(extraction_grid_1d[:, 0])
        x_pixels_max = np.max(extraction_grid_1d[:, 1])
        x_pixels_min = np.min(extraction_grid_1d[:, 1])
        return (
            (((y_pixels_max + y_pixels_min) - 1.0) / 2.0),
            (((x_pixels_max + x_pixels_min) - 1.0) / 2.0),
        )

    @property
    def zoom_offset_pixels(self):
        if self.pixel_scales is None:
            return self.geometry.central_pixel_coordinates
        return (
            (self.zoom_centre[0] - self.geometry.central_pixel_coordinates[0]),
            (self.zoom_centre[1] - self.geometry.central_pixel_coordinates[1]),
        )

    @property
    def zoom_offset_scaled(self):
        return (
            ((-self.pixel_scales[0]) * self.zoom_offset_pixels[0]),
            (self.pixel_scales[1] * self.zoom_offset_pixels[1]),
        )

    @property
    def zoom_region(self):
        """
        The zoomed rectangular region corresponding to the square encompassing all unmasked values. This zoomed
        extraction region is a squuare, even if the mask is rectangular.

        This is used to zoom in on the region of an image that is used in an analysis for visualization.
        """
        where = np.array(np.where(np.invert(self.astype("bool"))))
        (y0, x0) = np.amin(where, axis=1)
        (y1, x1) = np.amax(where, axis=1)
        ylength = y1 - y0
        xlength = x1 - x0
        if ylength > xlength:
            length_difference = ylength - xlength
            x1 += int((length_difference / 2.0))
            x0 -= int((length_difference / 2.0))
        elif xlength > ylength:
            length_difference = xlength - ylength
            y1 += int((length_difference / 2.0))
            y0 -= int((length_difference / 2.0))
        return [y0, (y1 + 1), x0, (x1 + 1)]

    @property
    def zoom_shape_native(self):
        region = self.zoom_region
        return ((region[1] - region[0]), (region[3] - region[2]))

    @property
    def zoom_mask_unmasked(self):
        """
        The scaled-grid of (y,x) coordinates of every pixel.

        This is defined from the top-left corner, such that the first pixel at location [0, 0] will have a negative x
        value y value in scaled units.
        """
        return Mask2D.all_false(
            shape_native=self.zoom_shape_native,
            pixel_scales=self.pixel_scales,
            origin=self.zoom_offset_scaled,
        )

    @property
    def is_circular(self):
        """
        Returns whether the mask is circular or not.

        This is performed by taking the central row and column of the mask (based on the mask centre) and counting
        the number of unmasked pixels. If the number of unmasked pixels is the same, the mask is circular.

        This function does not support rectangular masks and an exception will be raised if the pixel scales in each
        direction are different.
        """
        if self.pixel_scales[0] != self.pixel_scales[1]:
            raise exc.MaskException(
                """
                The is_circular function cannot be called for a mask with different pixel scales in each dimension
                (e.g. it does not support rectangular masks.
                """
            )
        pixel_coordinates_2d = self.geometry.pixel_coordinates_2d_from(
            scaled_coordinates_2d=self.mask_centre
        )
        central_row_pixels = sum(np.invert(self[pixel_coordinates_2d[0], :]))
        central_column_pixels = sum(np.invert(self[:, pixel_coordinates_2d[1]]))
        return central_row_pixels == central_column_pixels

    @cached_property
    def circular_radius(self):
        """
        Returns the radius in scaled units of a circular mask.

        This is performed by taking the central row of the mask (based on the mask centre) and counting the number of
        unmasked pixels. The radius is then half the number of unmasked pixels times the pixel scale.

        The mask is first checked that it is circular using the `is_circular` property, with an exception raised if
        it is not.

        This function does not support rectangular masks and an exception will be raised if the pixel scales in each
        direction are different.

        Returns
        -------
        The circular radius of the mask in scaled units.
        """
        if not self.is_circular:
            raise exc.MaskException(
                """
                A circular radius can only be computed for a circular mask.
                
                The `is_circular` property of this mask has returned False, indicating the mask is not circular.
                """
            )
        pixel_coordinates_2d = self.geometry.pixel_coordinates_2d_from(
            scaled_coordinates_2d=self.mask_centre
        )
        central_row_pixels = sum(np.invert(self[pixel_coordinates_2d[0], :]))
        return (central_row_pixels * self.pixel_scales[0]) / 2.0
