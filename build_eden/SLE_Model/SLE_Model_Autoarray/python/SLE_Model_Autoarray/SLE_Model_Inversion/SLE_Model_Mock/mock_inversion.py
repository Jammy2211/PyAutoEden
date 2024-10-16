import numpy as np
from typing import List
from SLE_Model_Autoarray.SLE_Model_Inversion.SLE_Model_Inversion.dataset_interface import (
    DatasetInterface,
)
from SLE_Model_Autoarray.SLE_Model_Inversion.SLE_Model_Inversion.abstract import (
    AbstractInversion,
)
from SLE_Model_Autoarray.SLE_Model_Inversion.SLE_Model_Inversion.settings import (
    SettingsInversion,
)
from SLE_Model_Autoarray.preloads import Preloads


class MockInversion(AbstractInversion):
    def __init__(
        self,
        data=None,
        noise_map=None,
        linear_obj_list=None,
        operated_mapping_matrix=None,
        data_vector=None,
        curvature_matrix=None,
        data_vector_mapper=None,
        curvature_matrix_mapper_diag=None,
        mapper_operated_mapping_matrix_dict=None,
        regularization_matrix=None,
        curvature_reg_matrix=None,
        reconstruction=None,
        reconstruction_dict=None,
        mapped_reconstructed_data_dict=None,
        mapped_reconstructed_image_dict=None,
        errors=None,
        errors_dict=None,
        regularization_term=None,
        log_det_curvature_reg_matrix_term=None,
        log_det_regularization_matrix_term=None,
        settings=SettingsInversion(),
        preloads=Preloads(),
    ):
        dataset = DatasetInterface(data=data, noise_map=noise_map)
        super().__init__(
            dataset=dataset,
            linear_obj_list=(linear_obj_list or []),
            settings=settings,
            preloads=preloads,
        )
        self._operated_mapping_matrix = operated_mapping_matrix
        self._data_vector = data_vector
        self._regularization_matrix = regularization_matrix
        self._curvature_matrix = curvature_matrix
        self.__data_vector_mapper = data_vector_mapper
        self.__curvature_matrix_mapper_diag = curvature_matrix_mapper_diag
        self._mapper_operated_mapping_matrix_dict = mapper_operated_mapping_matrix_dict
        self._curvature_reg_matrix = curvature_reg_matrix
        self._reconstruction = reconstruction
        self._reconstruction_dict = reconstruction_dict
        self._mapped_reconstructed_data_dict = mapped_reconstructed_data_dict
        self._mapped_reconstructed_image_dict = mapped_reconstructed_image_dict
        self._errors = errors
        self._errors_dict = errors_dict
        self._regularization_term = regularization_term
        self._log_det_curvature_reg_matrix_term = log_det_curvature_reg_matrix_term
        self._log_det_regularization_matrix_term = log_det_regularization_matrix_term

    @property
    def operated_mapping_matrix(self):
        if self._operated_mapping_matrix is None:
            return super().operated_mapping_matrix
        return self._operated_mapping_matrix

    @property
    def data_vector(self):
        if self._data_vector is None:
            return super().data_vector
        return self._data_vector

    @property
    def regularization_matrix(self):
        if self._regularization_matrix is None:
            return super().regularization_matrix
        return self._regularization_matrix

    @property
    def curvature_matrix(self):
        if self._curvature_matrix is None:
            return super().curvature_matrix
        return self._curvature_matrix

    @property
    def _data_vector_mapper(self):
        if self.__data_vector_mapper is None:
            return super()._data_vector_mapper
        return self.__data_vector_mapper

    @property
    def _curvature_matrix_mapper_diag(self):
        if self.__curvature_matrix_mapper_diag is None:
            return super()._curvature_matrix_mapper_diag
        return self.__curvature_matrix_mapper_diag

    @property
    def mapper_operated_mapping_matrix_dict(self):
        if self._mapper_operated_mapping_matrix_dict is None:
            return super().mapper_operated_mapping_matrix_dict
        return self._mapper_operated_mapping_matrix_dict

    @property
    def curvature_reg_matrix(self):
        return self._curvature_reg_matrix

    @property
    def reconstruction(self):
        if self._reconstruction is None:
            return super().reconstruction
        return self._reconstruction

    @property
    def reconstruction_dict(self):
        if self._reconstruction_dict is None:
            return super().reconstruction_dict
        return self._reconstruction_dict

    @property
    def mapped_reconstructed_data_dict(self):
        """
        Using the reconstructed source pixel fluxes we map each source pixel flux back to the image plane and
        reconstruct the image data.

        This uses the unique mappings of every source pixel to image pixels, which is a quantity that is already
        computed when using the w-tilde formalism.

        Returns
        -------
        Array2D
            The reconstructed image data which the inversion fits.
        """
        if self._mapped_reconstructed_data_dict is None:
            return super().mapped_reconstructed_data_dict
        return self._mapped_reconstructed_data_dict

    @property
    def mapped_reconstructed_image_dict(self):
        """
        Using the reconstructed source pixel fluxes we map each source pixel flux back to the image plane and
        reconstruct the image image.

        This uses the unique mappings of every source pixel to image pixels, which is a quantity that is already
        computed when using the w-tilde formalism.

        Returns
        -------
        Array2D
            The reconstructed image image which the inversion fits.
        """
        if self._mapped_reconstructed_image_dict is None:
            return super().mapped_reconstructed_image_dict
        return self._mapped_reconstructed_image_dict

    @property
    def errors(self):
        if self._errors is None:
            return super().errors
        return self._errors

    @property
    def errors_dict(self):
        if self._errors_dict is None:
            return super().errors_dict
        return self._errors_dict

    @property
    def regularization_term(self):
        if self._regularization_term is None:
            return super().regularization_term
        return self._regularization_term

    @property
    def log_det_curvature_reg_matrix_term(self):
        if self._log_det_curvature_reg_matrix_term is None:
            return super().log_det_curvature_reg_matrix_term
        return self._log_det_curvature_reg_matrix_term

    @property
    def log_det_regularization_matrix_term(self):
        if self._log_det_regularization_matrix_term is None:
            return super().log_det_regularization_matrix_term
        return self._log_det_regularization_matrix_term
