from typing import Optional, List

from VIS_CTI_Autoconf.dictable import from_json

from SHE_ArCTICPy import CCDPhase
from SHE_ArCTICPy import TrapInstantCapture
from SHE_ArCTICPy import PixelBounce


class AbstractCTI:
    @staticmethod
    def from_json(file_path):
        return from_json(file_path=file_path)

    @property
    def trap_list(self):
        raise NotImplementedError

    @property
    def delta_ellipticity(self):
        return sum([trap.delta_ellipticity for trap in self.trap_list])


class CTI1D(AbstractCTI):
    def __init__(
        self,
        trap_list: Optional[List[TrapInstantCapture]] = None,
        ccd: Optional[CCDPhase] = None,
        pixel_bounce_list : Optional[List[PixelBounce]] = None,
    ):
        """
        An object which determines the behaviour of CTI during 1D clocking.

        This includes the traps that capture and trail electrons and the CCD volume filling behaviour.

        Parameters
        ----------
        trap_list
            The traps on the dataset that capture and release electrons during clocking.
        ccd
            The CCD volume filling parameterization which dictates how an electron cloud fills pixels and thus
            how it is subject to traps.
        pixel_bounce_list
            List of pixel bounce objects which describe the behaviour of electrons due to electronic pixel bounce.
        """
        self._trap_list = trap_list
        self.ccd = ccd
        self.pixel_bounce_list = pixel_bounce_list

    @property
    def trap_list(self):

        return self._trap_list


class CTI2D(AbstractCTI):
    def __init__(
        self,
        parallel_trap_list: Optional[List[TrapInstantCapture]] = None,
        parallel_ccd: Optional[CCDPhase] = None,
        serial_trap_list: Optional[List[TrapInstantCapture]] = None,
        serial_ccd: Optional[CCDPhase] = None,
        pixel_bounce_list : Optional[List[PixelBounce]] = None,
    ):
        """
        An object which determines the behaviour of CTI during 2D parallel and serial clocking.

        This includes the traps that capture and trail electrons and the CCD volume filling behaviour.

        Parameters
        ----------
        parallel_trap_list
            The traps on the dataset that capture and release electrons during parallel clocking.
        parallel_ccd
            The CCD volume filling parameterization which dictates how an electron cloud fills pixel in the parallel
             direction and thus how it is subject to traps.
        serial_trap_list
            The traps on the dataset that capture and release electrons during serial clocking.
        serial_ccd
            The CCD volume filling parameterization which dictates how an electron cloud fills pixel in the serial
             direction and thus how it is subject to traps.
        pixel_bounce_list
            List of pixel bounce objects which describe the behaviour of electrons due to electronic pixel bounce.
        """
        self.parallel_trap_list = parallel_trap_list
        self.parallel_ccd = parallel_ccd
        self.serial_trap_list = serial_trap_list
        self.serial_ccd = serial_ccd
        self.pixel_bounce_list = pixel_bounce_list

    @property
    def trap_list(self) -> List[TrapInstantCapture]:
        """
        Combine the parallel and serial trap lists to make an overall list of traps in the model.

        This is not a straight forward list addition, because **PyAutoFit** model's store the `parallel_traps` and
        `serial_traps` entries as a `ModelInstance`. This object does not allow for straight forward list addition.
        """
        parallel_traps = self.parallel_trap_list or []
        serial_traps = self.serial_trap_list or []

        return [trap for trap in parallel_traps] + [trap for trap in serial_traps]



