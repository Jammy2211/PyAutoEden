import logging
import numpy as np
from VIS_CTI_Autoarray import exc

logging.basicConfig()
logger = logging.getLogger(__name__)


class AbstractMask(np.ndarray):
    pixel_scales = None

    def __new__(cls, mask, origin, pixel_scales, sub_size=1, *args, **kwargs):
        """
        An abstract class for a mask that represents data structure that can be in 1D, 2D or other shapes.

        When applied to data it extracts or masks the unmasked image pixels corresponding to mask entries
        that are (`False` or 0).

        The mask also defines the geometry of the data structure it is paired with, for example how its pixels convert
        to physical units via the pixel_scales and origin parameters and a sub-grid which is used for
        perform calculations via super-sampling.

        Parameters
        ----------
        mask
            The ndarray containing the bool's representing the mask, where `False` signifies an entry is
            unmasked and used in calculations.
        pixel_scales
            The scaled units to pixel units conversion factors of every pixel. If this is input as a float, it is
            converted to a (float, float) structure.
        origin
            The origin of the mask's coordinate system in scaled units.
        """
        mask = mask.astype("bool")
        obj = mask.view(cls)
        obj.sub_size = sub_size
        obj.pixel_scales = pixel_scales
        obj.origin = origin
        return obj

    def __array_finalize__(self, obj):
        if isinstance(obj, AbstractMask):
            self.sub_size = obj.sub_size
            self.pixel_scales = obj.pixel_scales
            self.origin = obj.origin
        else:
            self.sub_size = 1
            self.pixel_scales = None

    def __reduce__(self):
        pickled_state = super().__reduce__()
        class_dict = {}
        for (key, value) in self.__dict__.items():
            class_dict[key] = value
        new_state = pickled_state[2] + (class_dict,)
        return (pickled_state[0], pickled_state[1], new_state)

    def __setstate__(self, state):
        for (key, value) in state[(-1)].items():
            setattr(self, key, value)
        super().__setstate__(state[0:(-1)])

    @property
    def pixel_scale(self):
        """
        For a mask with dimensions two or above check that are pixel scales are the same, and if so return this
        single value as a float.
        """
        for pixel_scale in self.pixel_scales:
            if pixel_scale != self.pixel_scales[0]:
                raise exc.MaskException(
                    "Cannot return a pixel_scale for a grid where each dimension has a different pixel scale (e.g. pixel_scales[0] != pixel_scales[1])"
                )
        return self.pixel_scales[0]

    @property
    def dimensions(self):
        return len(self.shape)

    @property
    def sub_length(self):
        """
        The total number of sub-pixels in a give pixel,

        For example, a sub-size of 3x3 means every pixel has 9 sub-pixels.
        """
        return int((self.sub_size ** self.dimensions))

    @property
    def sub_fraction(self):
        """
        The fraction of the area of a pixel every sub-pixel contains.

        For example, a sub-size of 3x3 mean every pixel contains 1/9 the area.
        """
        return 1.0 / self.sub_length

    def output_to_fits(self, file_path, overwrite=False):
        raise NotImplementedError()

    @property
    def pixels_in_mask(self):
        """
        The total number of unmasked pixels (values are `False`) in the mask.
        """
        return int((np.size(self) - np.sum(self)))

    @property
    def is_all_true(self):
        """
        Returns `True` if all pixels in a mask are `True`, else returns `False`.
        """
        return self.pixels_in_mask == 0

    @property
    def is_all_false(self):
        """
        Returns `False` if all pixels in a mask are `False`, else returns `True`.
        """
        return self.pixels_in_mask == np.size(self)

    @property
    def sub_pixels_in_mask(self):
        """
        The total number of unmasked sub-pixels (values are `False`) in the mask.
        """
        return (self.sub_size ** self.dimensions) * self.pixels_in_mask

    @property
    def shape_slim(self):
        """
        The 1D shape of the mask, which is equivalent to the total number of unmasked pixels in the mask.
        """
        return self.pixels_in_mask

    @property
    def sub_shape_slim(self):
        """
        The 1D shape of the mask's sub-grid, which is equivalent to the total number of unmasked pixels in the mask.
        """
        return int((self.pixels_in_mask * (self.sub_size ** self.dimensions)))

    def mask_new_sub_size_from(self, mask, sub_size=1):
        """
        Returns the mask on the same scaled coordinate system but with a sub-grid of an inputsub_size.
        """
        return self.__class__(
            mask=mask,
            sub_size=sub_size,
            pixel_scales=self.pixel_scales,
            origin=self.origin,
        )
