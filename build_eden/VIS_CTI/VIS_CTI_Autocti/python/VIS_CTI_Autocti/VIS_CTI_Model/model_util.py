from arcticpy.src import ccd
from arcticpy.src import traps
from typing import Optional, List


class CTI1D:
    def __init__(self, traps=None, ccd=None):
        self.traps = traps
        self.ccd = ccd


class CTI2D:
    def __init__(
        self, parallel_traps=None, parallel_ccd=None, serial_traps=None, serial_ccd=None
    ):
        self.parallel_traps = parallel_traps
        self.parallel_ccd = parallel_ccd
        self.serial_traps = serial_traps
        self.serial_ccd = serial_ccd


def is_parallel_fit(model):
    if (model.parallel_ccd is not None) and (model.serial_ccd is None):
        return True
    return False


def is_serial_fit(model):
    if (model.parallel_ccd is None) and (model.serial_ccd is not None):
        return True
    return False


def is_parallel_and_serial_fit(model):
    if (model.parallel_ccd is not None) and (model.serial_ccd is not None):
        return True
    return False
