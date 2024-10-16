import numpy as np
from typing import Tuple
from SLE_Model_Autogalaxy.SLE_Model_Cosmology.wrap import Planck15
from SLE_Model_Autogalaxy.SLE_Model_Profiles.SLE_Model_Mass.SLE_Model_Point.point import (
    PointMass,
)


class SMBH(PointMass):
    def __init__(
        self,
        centre=(0.0, 0.0),
        mass=10000000000.0,
        redshift_object=0.5,
        redshift_source=1.0,
    ):
        """
        Represents a supermassive black hole (SMBH).

        This uses the `PointMass` mass profile to represent the SMBH, where the SMBH mass in converted to the
        `PointMass` Einstein radius value.

        Parameters
        ----------
        centre
            The (y,x) arc-second coordinates of the profile centre.
        mass
            The mass of the SMBH in solar masses.
        redshift_object
            The redshift of the SMBH, which is used to convert its mass to an Einstein radius.
        redshift_source
            The redshift of the source galaxy, which is used to convert the mass of the SMBH to an Einstein radius.
        """
        self.mass = mass
        cosmology = Planck15()
        critical_surface_density = (
            cosmology.critical_surface_density_between_redshifts_from(
                redshift_0=redshift_object, redshift_1=redshift_source
            )
        )
        mass_angular = mass / critical_surface_density
        einstein_radius = np.sqrt((mass_angular / np.pi))
        super().__init__(centre=centre, einstein_radius=einstein_radius)
        self.redshift_object = redshift_object
        self.redshift_source = redshift_source
