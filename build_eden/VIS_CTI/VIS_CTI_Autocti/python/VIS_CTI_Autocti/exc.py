from VIS_CTI_Autofit import exc
from VIS_CTI_Autoarray.exc import (
    ArrayException,
    MaskException,
    FrameException,
    RegionException,
)


class DatasetException(Exception):
    pass


class PatternLineException(Exception):
    pass


class LayoutException(Exception):
    pass


class PlottingException(Exception):
    pass


class FittingException(Exception):
    pass


class PriorException(exc.FitException):
    pass


class ClockerException(Exception):
    pass
