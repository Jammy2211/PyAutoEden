import numpy as np
from typing import Dict, List, Optional
from SLE_Model_Autoarray.SLE_Model_Inversion.SLE_Model_Inversion.abstract import (
    AbstractInversion,
)
from SLE_Model_Autoarray.SLE_Model_Mask.mask_2d import Mask2D
from SLE_Model_Autoarray.SLE_Model_Inversion.SLE_Model_LinearObj.linear_obj import (
    LinearObj,
)
from SLE_Model_Autoarray.SLE_Model_Inversion.SLE_Model_Inversion.settings import (
    SettingsInversion,
)
from SLE_Model_Autoarray.SLE_Model_Operators.transformer import TransformerNUFFT
from SLE_Model_Autoarray.preloads import Preloads
from SLE_Model_Autoarray.SLE_Model_Structures.SLE_Model_Arrays.uniform_2d import Array2D
from SLE_Model_Autoarray.SLE_Model_Structures.visibilities import Visibilities
from SLE_Model_Autoarray.SLE_Model_Structures.visibilities import VisibilitiesNoiseMap
from SLE_Model_Autoarray.SLE_Model_Inversion.SLE_Model_Inversion import inversion_util
from SLE_Model_Autoarray.numba_util import profile_func


class AbstractInversionInterferometer(AbstractInversion):
    def __init__(
        self,
        data,
        noise_map,
        transformer,
        linear_obj_list,
        settings=SettingsInversion(),
        preloads=Preloads(),
        profiling_dict=None,
    ):
        """
        Constructs linear equations (via vectors and matrices) which allow for sets of simultaneous linear equations
        to be solved (see `inversion.inversion.abstract.AbstractInversion` for a full description).

        A linear object describes the mappings between values in observed `data` and the linear object's model via its
        `mapping_matrix`. This class constructs linear equations for `Interferometer` objects, where the data is an
        an array of visibilities and the mappings include a non-uniform fast Fourier transform operation described by
        the interferometer dataset's transformer.

        Parameters
        ----------
        noise_map
            The noise-map of the observed interferometer data which values are solved for.
        transformer
            The transformer which performs a non-uniform fast Fourier transform operations on the mapping matrix
            with the interferometer data's transformer.
        linear_obj_list
            The linear objects used to reconstruct the data's observed values. If multiple linear objects are passed
            the simultaneous linear equations are combined and solved simultaneously.
        profiling_dict
            A dictionary which contains timing of certain functions calls which is used for profiling.
        """
        super().__init__(
            data=data,
            noise_map=noise_map,
            linear_obj_list=linear_obj_list,
            settings=settings,
            preloads=preloads,
            profiling_dict=profiling_dict,
        )
        self.transformer = transformer

    @property
    def mask(self):
        return self.transformer.real_space_mask

    @property
    def operated_mapping_matrix_list(self):
        """
        The `operated_mapping_matrix` of a linear object describes the mappings between the observed data's values
        and the linear objects model, including a non-uniform fast Fourier transform operation.

        This is used to construct the simultaneous linear equations which reconstruct the data.

        This property returns the a list of each linear object's transformed mapping matrix.
        """
        return [
            self.transformer.transform_mapping_matrix(
                mapping_matrix=linear_obj.mapping_matrix
            )
            for linear_obj in self.linear_obj_list
        ]

    @property
    @profile_func
    def mapped_reconstructed_image_dict(self):
        """
        When constructing the simultaneous linear equations (via vectors and matrices) the quantities of each individual
        linear object (e.g. their `mapping_matrix`) are combined into single ndarrays. This does not track which
        quantities belong to which linear objects, therefore the linear equation's solutions (which are returned as
        ndarrays) do not contain information on which linear object(s) they correspond to.

        For example, consider if two `Mapper` objects with 50 and 100 source pixels are used in an `Inversion`.
        The `reconstruction` (which contains the solved for source pixels values) is an ndarray of shape [150], but
        the ndarray itself does not track which values belong to which `Mapper`.

        This function converts an ndarray of a `reconstruction` to a dictionary of ndarrays containing each linear
        object's reconstructed images, where the keys are the instances of each mapper in the inversion.

        For the linear equations which fit interferometer datasets, the reconstructed data is its visibilities. Thus,
        the reconstructed image is computed separately by performing a non-uniform fast Fourier transform which maps
        the `reconstruction`'s values to real space.

        Parameters
        ----------
        reconstruction
            The reconstruction (in the source frame) whose values are mapped to a dictionary of values for each
            individual mapper (in the image-plane).
        """
        mapped_reconstructed_image_dict = {}
        reconstruction_dict = self.source_quantity_dict_from(
            source_quantity=self.reconstruction
        )
        for linear_obj in self.linear_obj_list:
            reconstruction = reconstruction_dict[linear_obj]
            mapped_reconstructed_image = (
                inversion_util.mapped_reconstructed_data_via_mapping_matrix_from(
                    mapping_matrix=linear_obj.mapping_matrix,
                    reconstruction=reconstruction,
                )
            )
            mapped_reconstructed_image = Array2D(
                values=mapped_reconstructed_image, mask=self.mask.derive_mask.sub_1
            )
            mapped_reconstructed_image_dict[linear_obj] = mapped_reconstructed_image
        return mapped_reconstructed_image_dict
