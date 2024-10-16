from typing import Tuple
from SLE_Model_Autogalaxy.SLE_Model_Profiles.SLE_Model_Light.SLE_Model_Linear.abstract import (
    LightProfileLinear,
)
from SLE_Model_Autogalaxy.SLE_Model_Profiles.SLE_Model_Light import (
    SLE_Model_Standard as lp,
)


class Moffat(lp.Moffat, LightProfileLinear):
    def __init__(self, centre=(0.0, 0.0), ell_comps=(0.0, 0.0), alpha=0.5, beta=2.0):
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
            The first and second ellipticity components of the elliptical coordinate system, (see the module
        alpha
            Scales the overall size of the Moffat profile and for a PSF typically corresponds to the FWHM / 2.
        beta
            Scales the wings at the outskirts of the Moffat profile, where smaller values imply heavier wings and it
            tends to a Gaussian as beta goes to infinity.
        """
        super().__init__(
            centre=centre, ell_comps=ell_comps, intensity=1.0, alpha=alpha, beta=beta
        )


class MoffatSph(Moffat):
    def __init__(self, centre=(0.0, 0.0), alpha=0.5, beta=2.0):
        """
        The spherical Moffat light profile, which is commonly used to model the Point Spread Function of
        Astronomy observations.

        This form of the MOffat profile is a reparameterizaiton of the original formalism given by
        https://ui.adsabs.harvard.edu/abs/1969A%26A.....3..455M/abstract. The actual profile itself is identical.

        Parameters
        ----------
        centre
            The (y,x) arc-second coordinates of the profile centre.
        alpha
            Scales the overall size of the Moffat profile and for a PSF typically corresponds to the FWHM / 2.
        beta
            Scales the wings at the outskirts of the Moffat profile, where smaller values imply heavier wings and it
            tends to a Gaussian as beta goes to infinity.
        """
        super().__init__(centre=centre, ell_comps=(0.0, 0.0), alpha=alpha, beta=beta)
