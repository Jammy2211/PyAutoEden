from typing import Tuple
import numpy as np
from SLE_Model_Autogalaxy.SLE_Model_Profiles.SLE_Model_Mass.SLE_Model_Dark.nfw import (
    NFWSph,
)
from SLE_Model_Autogalaxy.SLE_Model_Profiles.SLE_Model_Mass.SLE_Model_Dark.nfw import (
    NFW,
)
from SLE_Model_Autogalaxy.SLE_Model_Profiles.SLE_Model_Mass.SLE_Model_Dark import (
    mcr_util,
)


class NFWMCRScatterLudlowSph(NFWSph):
    def __init__(
        self,
        centre=(0.0, 0.0),
        mass_at_200=1000000000.0,
        scatter_sigma=0.0,
        redshift_object=0.5,
        redshift_source=1.0,
    ):
        self.mass_at_200 = mass_at_200
        self.scatter_sigma = scatter_sigma
        self.redshift_object = redshift_object
        self.redshift_source = redshift_source
        (
            kappa_s,
            scale_radius,
            radius_at_200,
        ) = mcr_util.kappa_s_and_scale_radius_for_ludlow(
            mass_at_200=mass_at_200,
            scatter_sigma=scatter_sigma,
            redshift_object=redshift_object,
            redshift_source=redshift_source,
        )
        super().__init__(centre=centre, kappa_s=kappa_s, scale_radius=scale_radius)


class NFWMCRScatterLudlow(NFW):
    def __init__(
        self,
        centre=(0.0, 0.0),
        ell_comps=(0.0, 0.0),
        mass_at_200=1000000000.0,
        scatter_sigma=0.0,
        redshift_object=0.5,
        redshift_source=1.0,
    ):
        self.mass_at_200 = mass_at_200
        self.scatter_sigma = scatter_sigma
        self.redshift_object = redshift_object
        self.redshift_source = redshift_source
        (
            kappa_s,
            scale_radius,
            radius_at_200,
        ) = mcr_util.kappa_s_and_scale_radius_for_ludlow(
            mass_at_200=mass_at_200,
            scatter_sigma=scatter_sigma,
            redshift_object=redshift_object,
            redshift_source=redshift_source,
        )
        """
        #Make correction that Andrew proposed
        fac = np.sqrt(ell_comps[1] ** 2 + ell_comps[0] ** 2)
        if fac > 0.999:
            fac = 0.999  # avoid unphysical solution
        # if fac > 1: print('unphysical e1,e2')
        axis_ratio = (1 - fac) / (1 + fac)
        scale_radius = scale_radius / np.sqrt(axis_ratio)
        
        print('With Correction')
        """
        super().__init__(
            centre=centre,
            ell_comps=ell_comps,
            kappa_s=kappa_s,
            scale_radius=scale_radius,
        )
