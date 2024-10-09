from astropy import cosmology as cosmo
from SLE_Model_Autogalaxy.SLE_Model_Cosmology.wrap import FlatLambdaCDM
from SLE_Model_Autogalaxy.SLE_Model_Cosmology.wrap import FlatwCDM


class Planck15Om0(FlatLambdaCDM):
    def __init__(self, Om0=0.3075):
        planck15 = cosmo.Planck15
        super().__init__(
            H0=planck15.H0,
            Om0=Om0,
            Tcmb0=planck15.Tcmb0,
            Neff=planck15.Neff,
            m_nu=planck15.m_nu,
            Ob0=planck15.Ob0,
            name=planck15.name,
        )


class Planck15FlatwCDM(FlatwCDM):
    def __init__(self, Om0=0.3075, w0=(-1.0)):
        planck15 = cosmo.Planck15
        super().__init__(
            H0=planck15.H0,
            Om0=Om0,
            w0=w0,
            Tcmb0=planck15.Tcmb0,
            Neff=planck15.Neff,
            m_nu=planck15.m_nu,
            Ob0=planck15.Ob0,
            name=planck15.name,
        )
