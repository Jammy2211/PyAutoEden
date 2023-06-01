from __future__ import annotations
from abc import ABC
from abc import abstractmethod
import numpy as np
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from SLE_Model_Autoarray.SLE_Model_Structures.abstract_structure import Structure
from SLE_Model_Autoarray.SLE_Model_Structures.SLE_Model_Arrays import array_2d_util


class AbstractNDArray(np.ndarray, ABC):
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
    @abstractmethod
    def native(self):
        """
        Returns the data structure in its `native` format which contains all unmaksed values to the native dimensions.
        """

    def output_to_fits(self, file_path, overwrite=False):
        """
        Output the grid to a .fits file.

        Parameters
        ----------
        file_path
            The path the file is output to, including the filename and the .fits extension, e.g. '/path/to/filename.fits'
        overwrite
            If a file already exists at the path, if overwrite=True it is overwritten else an error is raised.
        """
        array_2d_util.numpy_array_2d_to_fits(
            array_2d=self.native, file_path=file_path, overwrite=overwrite
        )