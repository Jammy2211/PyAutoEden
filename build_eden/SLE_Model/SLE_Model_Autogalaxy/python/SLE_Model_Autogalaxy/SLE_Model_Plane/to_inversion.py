from __future__ import annotations
from typing import TYPE_CHECKING, Dict, List, Optional, Type, Union

if TYPE_CHECKING:
    from SLE_Model_Autogalaxy.SLE_Model_Plane.plane import Plane
from SLE_Model_Autoconf import cached_property
import SLE_Model_Autoarray as aa
from SLE_Model_Autoarray.SLE_Model_Inversion.SLE_Model_Pixelization.SLE_Model_Mappers.factory import (
    mapper_from,
)
from SLE_Model_Autoarray.SLE_Model_Inversion.SLE_Model_Inversion.factory import (
    inversion_unpacked_from,
)
from SLE_Model_Autogalaxy.SLE_Model_Profiles.SLE_Model_Light.SLE_Model_Linear import (
    LightProfileLinearObjFuncList,
)
from SLE_Model_Autogalaxy.SLE_Model_Profiles.SLE_Model_Light.basis import Basis
from SLE_Model_Autogalaxy.SLE_Model_Profiles.SLE_Model_Light.SLE_Model_Linear import (
    LightProfileLinear,
)
from SLE_Model_Autogalaxy.SLE_Model_Galaxy.galaxy import Galaxy
from SLE_Model_Autogalaxy.SLE_Model_Analysis.preloads import Preloads


class AbstractToInversion:
    def __init__(
        self,
        dataset=None,
        data=None,
        noise_map=None,
        w_tilde=None,
        settings_pixelization=aa.SettingsPixelization(),
        settings_inversion=aa.SettingsInversion(),
        preloads=Preloads(),
        profiling_dict=None,
    ):
        if dataset is not None:
            if dataset.noise_covariance_matrix is not None:
                raise aa.exc.InversionException(
                    """
                    You cannot perform an inversion (e.g. use a linear light profile or pixelization) 
                    if the dataset has a `noise_covariance_matrix`.
                    
                    This is because the linear algebra implementation is only valid under the assumption 
                    of independent gaussian noise.
                    """
                )
        self.dataset = dataset
        self.data = data
        self.noise_map = noise_map
        self.w_tilde = w_tilde
        self.settings_pixelization = settings_pixelization
        self.settings_inversion = settings_inversion
        self.preloads = preloads
        self.profiling_dict = profiling_dict

    def cls_light_profile_func_list_galaxy_dict_from(self, cls):
        raise NotImplementedError

    @cached_property
    def lp_linear_func_list_galaxy_dict(self):
        raise NotImplementedError

    @cached_property
    def mapper_galaxy_dict(self):
        raise NotImplementedError

    @cached_property
    def linear_obj_galaxy_dict(self):
        lp_linear_func_galaxy_dict = self.lp_linear_func_list_galaxy_dict
        mapper_galaxy_dict = self.mapper_galaxy_dict
        return {**lp_linear_func_galaxy_dict, **mapper_galaxy_dict}

    @cached_property
    def linear_obj_list(self):
        return list(self.linear_obj_galaxy_dict.keys())

    @cached_property
    def regularization_list(self):
        return [linear_obj.regularization for linear_obj in self.linear_obj_list]


class PlaneToInversion(AbstractToInversion):
    def __init__(
        self,
        plane,
        dataset=None,
        data=None,
        noise_map=None,
        w_tilde=None,
        grid=None,
        blurring_grid=None,
        grid_pixelization=None,
        settings_pixelization=aa.SettingsPixelization(),
        settings_inversion=aa.SettingsInversion(),
        preloads=aa.Preloads(),
        profiling_dict=None,
    ):
        self.plane = plane
        super().__init__(
            dataset=dataset,
            data=data,
            noise_map=noise_map,
            w_tilde=w_tilde,
            settings_pixelization=settings_pixelization,
            settings_inversion=settings_inversion,
            preloads=preloads,
            profiling_dict=profiling_dict,
        )
        if grid is not None:
            self.grid = grid
        elif dataset is not None:
            self.grid = dataset.grid
        else:
            self.grid = None
        if blurring_grid is not None:
            self.blurring_grid = blurring_grid
        elif dataset is not None:
            self.blurring_grid = dataset.blurring_grid
        else:
            self.blurring_grid = None
        if grid_pixelization is not None:
            self.grid_pixelization = grid_pixelization
        elif dataset is not None:
            self.grid_pixelization = dataset.grid_pixelization
        else:
            self.grid_pixelization = None

    def cls_light_profile_func_list_galaxy_dict_from(self, cls):
        if not self.plane.has(cls=cls):
            return {}
        lp_linear_func_galaxy_dict = {}
        for galaxy in self.plane.galaxies:
            if galaxy.has(cls=cls):
                for light_profile in galaxy.cls_list_from(cls=cls):
                    if isinstance(light_profile, LightProfileLinear):
                        light_profile_list = [light_profile]
                    else:
                        light_profile_list = light_profile.light_profile_list
                        light_profile_list = [
                            light_profile
                            for light_profile in light_profile_list
                            if isinstance(light_profile, LightProfileLinear)
                        ]
                    if len(light_profile_list) > 0:
                        lp_linear_func = LightProfileLinearObjFuncList(
                            grid=self.grid,
                            blurring_grid=self.blurring_grid,
                            convolver=self.dataset.convolver,
                            light_profile_list=light_profile_list,
                            regularization=light_profile.regularization,
                        )
                        lp_linear_func_galaxy_dict[lp_linear_func] = galaxy
        return lp_linear_func_galaxy_dict

    @cached_property
    def lp_linear_func_list_galaxy_dict(self):
        lp_linear_light_profile_func_list_galaxy_dict = (
            self.cls_light_profile_func_list_galaxy_dict_from(cls=LightProfileLinear)
        )
        lp_basis_func_list_galaxy_dict = (
            self.cls_light_profile_func_list_galaxy_dict_from(cls=Basis)
        )
        return {
            **lp_linear_light_profile_func_list_galaxy_dict,
            **lp_basis_func_list_galaxy_dict,
        }

    @cached_property
    def sparse_image_plane_grid_list(self):
        if not self.plane.has(cls=aa.Pixelization):
            return None
        return [
            pixelization.mesh.image_plane_mesh_grid_from(
                image_plane_data_grid=self.grid_pixelization,
                hyper_data=adapt_galaxy_image,
                settings=self.settings_pixelization,
            )
            for (pixelization, adapt_galaxy_image) in zip(
                self.plane.cls_list_from(cls=aa.Pixelization),
                self.plane.adapt_galaxies_with_pixelization_image_list,
            )
        ]

    def mapper_from(
        self,
        mesh,
        regularization,
        source_plane_mesh_grid,
        adapt_galaxy_image,
        image_plane_mesh_grid=None,
    ):
        mapper_grids = mesh.mapper_grids_from(
            source_plane_data_grid=self.grid_pixelization,
            source_plane_mesh_grid=source_plane_mesh_grid,
            image_plane_mesh_grid=image_plane_mesh_grid,
            hyper_data=adapt_galaxy_image,
            settings=self.settings_pixelization,
            preloads=self.preloads,
            profiling_dict=self.plane.profiling_dict,
        )
        return mapper_from(mapper_grids=mapper_grids, regularization=regularization)

    @cached_property
    def mapper_galaxy_dict(self):
        if not self.plane.has(cls=aa.Pixelization):
            return {}
        sparse_grid_list = self.sparse_image_plane_grid_list
        mapper_galaxy_dict = {}
        pixelization_list = self.plane.cls_list_from(cls=aa.Pixelization)
        galaxies_with_pixelization_list = self.plane.galaxies_with_cls_list_from(
            cls=aa.Pixelization
        )
        adapt_galaxy_image_list = self.plane.adapt_galaxies_with_pixelization_image_list
        for mapper_index in range(len(sparse_grid_list)):
            mapper = self.mapper_from(
                mesh=pixelization_list[mapper_index].mesh,
                regularization=pixelization_list[mapper_index].regularization,
                source_plane_mesh_grid=sparse_grid_list[mapper_index],
                adapt_galaxy_image=adapt_galaxy_image_list[mapper_index],
                image_plane_mesh_grid=sparse_grid_list[mapper_index],
            )
            galaxy = galaxies_with_pixelization_list[mapper_index]
            mapper_galaxy_dict[mapper] = galaxy
        return mapper_galaxy_dict

    @property
    def inversion(self):
        inversion = inversion_unpacked_from(
            dataset=self.dataset,
            data=self.data,
            noise_map=self.noise_map,
            w_tilde=self.w_tilde,
            linear_obj_list=self.linear_obj_list,
            settings=self.settings_inversion,
            preloads=self.preloads,
            profiling_dict=self.plane.profiling_dict,
        )
        inversion.linear_obj_galaxy_dict = self.linear_obj_galaxy_dict
        return inversion
