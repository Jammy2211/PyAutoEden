import numpy as np
from typing import Optional, Tuple
import SLE_Model_Autoarray as aa
from SLE_Model_Autogalaxy.SLE_Model_Profiles.SLE_Model_Light.abstract import (
    LightProfile,
)
from SLE_Model_Autogalaxy.SLE_Model_Profiles.SLE_Model_Light.decorators import (
    check_operated_only,
)


class Moffat(LightProfile):
    def __init__(
        self,
        centre=(0.0, 0.0),
        ell_comps=(0.0, 0.0),
        intensity=0.1,
        alpha=0.5,
        beta=2.0,
    ):
        """
        The elliptical Moffat light profile, which is commonly used to model the Point Spread Function of
        Astronomy observations.

        This form of the MOffat profile is a reparameterizaiton of the original formalism given by
        https://ui.adsabs.harvard.edu/abs/1969A%26A.....3..455M/abstract. The actual profile itself is identical.

        Parameters
        ----------
        centre
            The (y,x) arc-second coordinates of the profile centre.
        ell_comps
            The first and second ellipticity components of the elliptical coordinate system.
        intensity
            Overall intensity normalisation of the light profile (units are dimensionless and derived from the data
            the light profile's image is compared too, which is expected to be electrons per second).
        alpha
            Scales the overall size of the Moffat profile and for a PSF typically corresponds to the FWHM / 2.
        beta
            Scales the wings at the outskirts of the Moffat profile, where smaller values imply heavier wings and it
            tends to a Gaussian as beta goes to infinity.
        """
        super().__init__(centre=centre, ell_comps=ell_comps, intensity=intensity)
        self.alpha = alpha
        self.beta = beta

    def image_2d_via_radii_from(self, grid_radii):
        """
        Returns the 2D image of the Moffat light profile from a grid of coordinates which are the radial distance of
        each coordinate from the its `centre`.

        Note: sigma is divided by sqrt(q) here.

        Parameters
        ----------
        grid_radii
            The radial distances from the centre of the profile, for each coordinate on the grid.
        """
        return np.multiply(
            self._intensity,
            np.power(
                (
                    1
                    + np.square(
                        np.divide(grid_radii, (self.alpha / np.sqrt(self.axis_ratio)))
                    )
                ),
                (-self.beta),
            ),
        )

    @aa.over_sample
    @aa.grid_dec.to_array
    @check_operated_only
    @aa.grid_dec.transform
    @aa.grid_dec.relocate_to_radial_minimum
    def image_2d_from(self, grid, operated_only=None, **kwargs):
        """
        Returns the Moffat light profile's 2D image from a 2D grid of Cartesian (y,x) coordinates.

        If the coordinates have not been transformed to the profile's geometry (e.g. translated to the
        profile `centre`), this is performed automatically.

        Parameters
        ----------
        grid
            The 2D (y, x) coordinates in the original reference frame of the grid.

        Returns
        -------
        image
            The image of the Moffat evaluated at every (y,x) coordinate on the transformed grid.
        """
        return self.image_2d_via_radii_from(
            self.eccentric_radii_grid_from(grid=grid, **kwargs)
        )


class MoffatSph(Moffat):
    def __init__(self, centre=(0.0, 0.0), intensity=0.1, alpha=0.5, beta=2.0):
        """
        The spherical Moffat light profile:

        This form of the MOffat profile is a reparameterizaiton of the original formalism given by
        https://ui.adsabs.harvard.edu/abs/1969A%26A.....3..455M/abstract. The actual profile itself is identical.

        Parameters
        ----------
        centre
            The (y,x) arc-second coordinates of the profile centre.
        ell_comps
            The first and second ellipticity components of the elliptical coordinate system.
        intensity
            Overall intensity normalisation of the light profile (units are dimensionless and derived from the data
            the light profile's image is compared too, which is expected to be electrons per second).
        alpha
            Scales the overall size of the Moffat profile and for a PSF typically corresponds to the FWHM / 2.
        beta
            Scales the wings at the outskirts of the Moffat profile, where smaller values imply heavier wings and it
            tends to a Gaussian as beta goes to infinity.
        """
        super().__init__(centre=centre, intensity=intensity, alpha=alpha, beta=beta)
