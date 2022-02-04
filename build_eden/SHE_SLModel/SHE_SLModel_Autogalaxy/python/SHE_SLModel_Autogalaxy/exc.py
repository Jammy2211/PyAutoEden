import SHE_SLModel_Autofit as af
from SHE_SLModel_Autofit.exc import *
from SHE_SLModel_Autoarray.exc import *


class CosmologyException(Exception):
    pass


class ProfileException(Exception):
    pass


class GalaxyException(Exception):
    pass


class PlaneException(Exception):
    pass


class PlottingException(Exception):
    pass


class AnalysisException(Exception):
    pass


class PixelizationException(af.exc.FitException):
    pass


class UnitsException(Exception):
    pass


class SetupException(Exception):
    pass
