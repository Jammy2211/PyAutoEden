import numpy as np
from typing import Dict, List, Optional, Union
from SLE_Model_Autoconf import cached_property
from SLE_Model_Autoarray.SLE_Model_Dataset.SLE_Model_Interferometer.dataset import (
    Interferometer,
)
from SLE_Model_Autoarray.SLE_Model_Inversion.SLE_Model_Inversion.dataset_interface import (
    DatasetInterface,
)
from SLE_Model_Autoarray.SLE_Model_Inversion.SLE_Model_Inversion.SLE_Model_Interferometer.abstract import (
    AbstractInversionInterferometer,
)
from SLE_Model_Autoarray.SLE_Model_Inversion.SLE_Model_LinearObj.linear_obj import (
    LinearObj,
)
from SLE_Model_Autoarray.SLE_Model_Inversion.SLE_Model_Inversion.settings import (
    SettingsInversion,
)
from SLE_Model_Autoarray.preloads import Preloads
from SLE_Model_Autoarray.SLE_Model_Structures.visibilities import Visibilities
from SLE_Model_Autoarray.SLE_Model_Inversion.SLE_Model_Inversion.SLE_Model_Interferometer import (
    inversion_interferometer_util,
)
from SLE_Model_Autoarray.SLE_Model_Inversion.SLE_Model_Inversion import inversion_util
from SLE_Model_Autoarray.numba_util import profile_func


class InversionInterferometerMapping(AbstractInversionInterferometer):
    def __init__(
        self,
        dataset,
        linear_obj_list,
        settings=SettingsInversion(),
        preloads=Preloads(),
        run_time_dict=None,
    ):
        """
        Constructs linear equations (via vectors and matrices) which allow for sets of simultaneous linear equations
        to be solved (see `inversion.inversion.abstract.AbstractInversion` for a full description).

        A linear object describes the mappings between values in observed `data` and the linear object's model via its
        `mapping_matrix`. This class constructs linear equations for `Interferometer` objects, where the data is an
        an array of visibilities and the mappings include a non-uniform fast Fourier transform operation described by
        the interferometer dataset's transformer.

        This class uses the mapping formalism, which constructs the simultaneous linear equations using the
        `mapping_matrix` of every linear object.

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
        run_time_dict
            A dictionary which contains timing of certain functions calls which is used for profiling.
        """
        super().__init__(
            dataset=dataset,
            linear_obj_list=linear_obj_list,
            settings=settings,
            preloads=preloads,
            run_time_dict=run_time_dict,
        )

    @cached_property
    @profile_func
    def data_vector(self):
        """
        The `data_vector` is a 1D vector whose values are solved for by the simultaneous linear equations constructed
        by this object.

        The linear algebra is described in the paper https://arxiv.org/pdf/astro-ph/0302587.pdf), where the
        data vector is given by equation (4) and the letter D.

        If there are multiple linear objects their `operated_mapping_matrix` properties will have already been
        concatenated ensuring their `data_vector` values are solved for simultaneously.

        The calculation is described in more detail in `inversion_util.data_vector_via_transformed_mapping_matrix_from`.
        """
        return inversion_interferometer_util.data_vector_via_transformed_mapping_matrix_from(
            transformed_mapping_matrix=self.operated_mapping_matrix,
            visibilities=np.array(self.data),
            noise_map=np.array(self.noise_map),
        )

    @cached_property
    @profile_func
    def curvature_matrix(self):
        """
        The `curvature_matrix` is a 2D matrix which uses the mappings between the data and the linear objects to
        construct the simultaneous linear equations.

        The linear algebra is described in the paper https://arxiv.org/pdf/astro-ph/0302587.pdf, where the
        curvature matrix given by equation (4) and the letter F.

        If there are multiple linear objects their `operated_mapping_matrix` properties will have already been
        concatenated ensuring their `curvature_matrix` values are solved for simultaneously. This includes all
        diagonal and off-diagonal terms describing the covariances between linear objects.
        """
        real_curvature_matrix = inversion_util.curvature_matrix_via_mapping_matrix_from(
            mapping_matrix=self.operated_mapping_matrix.real,
            noise_map=self.noise_map.real,
        )
        imag_curvature_matrix = inversion_util.curvature_matrix_via_mapping_matrix_from(
            mapping_matrix=self.operated_mapping_matrix.imag,
            noise_map=self.noise_map.imag,
        )
        curvature_matrix = np.add(real_curvature_matrix, imag_curvature_matrix)
        if len(self.no_regularization_index_list) > 0:
            curvature_matrix = inversion_util.curvature_matrix_with_added_to_diag_from(
                curvature_matrix=curvature_matrix,
                no_regularization_index_list=self.no_regularization_index_list,
                value=self.settings.no_regularization_add_to_curvature_diag_value,
            )
        return curvature_matrix

    @property
    @profile_func
    def mapped_reconstructed_data_dict(self):
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

        To perform this mapping the `mapping_matrix` is used, which straightforwardly describes how every value of
        the `reconstruction` maps to pixels in the data-frame after the 2D non-uniform fast Fourier transformer
        operation has been performed.
        """
        mapped_reconstructed_data_dict = {}
        reconstruction_dict = self.source_quantity_dict_from(
            source_quantity=self.reconstruction
        )
        operated_mapping_matrix_list = self.operated_mapping_matrix_list
        for (index, linear_obj) in enumerate(self.linear_obj_list):
            reconstruction = reconstruction_dict[linear_obj]
            visibilities = (
                inversion_interferometer_util.mapped_reconstructed_visibilities_from(
                    transformed_mapping_matrix=operated_mapping_matrix_list[index],
                    reconstruction=reconstruction,
                )
            )
            visibilities = Visibilities(visibilities=visibilities)
            mapped_reconstructed_data_dict[linear_obj] = visibilities
        return mapped_reconstructed_data_dict
