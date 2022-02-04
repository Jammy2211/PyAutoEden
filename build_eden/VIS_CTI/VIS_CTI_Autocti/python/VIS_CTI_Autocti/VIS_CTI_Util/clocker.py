import numpy as np
from VIS_CTI_Autoarray.VIS_CTI_Structures.VIS_CTI_Arrays.VIS_CTI_OneD.array_1d import (
    Array1D,
)
from VIS_CTI_Autoarray.VIS_CTI_Structures.VIS_CTI_Arrays.VIS_CTI_TwoD.array_2d import (
    Array2D,
)
from VIS_CTI_Autocti import exc
from arcticpy.src import cti
from arcticpy.src.ccd import CCD
from arcticpy.src.ccd import CCDPhase
from arcticpy.src.roe import ROE


class AbstractClocker:
    def __init__(self, iterations=1, verbosity=0):
        """
        An abstract clocker, which wraps the c++ arctic CTI clocking algorithm in **PyAutoCTI**.

        Parameters
        ----------
        iterations
            The number of iterations used to correct CTI from an image.
        verbosity
            Whether to silence print statements and output from the c++ arctic call.
        """
        self.iterations = iterations
        self.verbosity = verbosity

    def ccd_from(self, ccd_phase):
        """
        Returns a `CCD` object from a `CCDPhase` object.

        The `CCDPhase` describes the volume-filling behaviour of the CCD and is therefore used as a model-component
        in CTI calibration. To call arctic it needs converting to a `CCD` object.

        Parameters
        ----------
        ccd_phase
            The ccd phase describing the volume-filling behaviour of the CCD.

        Returns
        -------
        A `CCD` object based on the input phase which is passed to the c++ arctic.
        """
        if ccd_phase is not None:
            return CCD(phases=[ccd_phase], fraction_of_traps_per_phase=[1.0])


class Clocker1D(AbstractClocker):
    def __init__(
        self,
        iterations=1,
        roe=ROE(),
        express=0,
        window_start=0,
        window_stop=(-1),
        verbosity=0,
    ):
        """
        Performs clocking of a 1D signal via the c++ arctic algorithm.

        This corresponds to a single row or column of a CCD in the parallel or serial direction. Given the notion of
        parallel and serial are not relevent in 1D, these prefixes are dropped from parameters (unlike the `Clocker2D`)
        object.

        Parameters
        ----------
        iterations
            The number of iterations used to correct CTI from an image.
        roe
            Contains parameters describing the read-out electronics of the CCD (e.g. CCD dwell times, charge injection
            clocking, etc.).
        express
            An integer factor describing how pixel-to-pixel transfers are combined into single transfers for
            efficiency (see: https://academic.oup.com/mnras/article/401/1/371/1006825).
        window_start
            The pixel index of the input image where arCTIc clocking begins, for example if `window_start=10` the
            first 10 pixels are omitted and not clocked.
        window_start
            The pixel index of the input image where arCTIc clocking ends, for example if `window_start=20` any
            pixels after the 20th pixel are omitted and not clocked.
        verbosity
            Whether to silence print statements and output from the c++ arctic call.
        """
        super().__init__(iterations=iterations, verbosity=verbosity)
        self.roe = roe
        self.express = express
        self.window_start = window_start
        self.window_stop = window_stop

    def add_cti(self, data, ccd=None, trap_list=None):
        if not any([trap_list]):
            raise exc.ClockerException(
                "No Trap species were passed to the add_cti method"
            )
        if not any([ccd]):
            raise exc.ClockerException("No CCD object was passed to the add_cti method")
        image_pre_cti_2d = Array2D.zeros(
            shape_native=(data.shape_native[0], 1), pixel_scales=data.pixel_scales
        ).native
        image_pre_cti_2d[:, 0] = data
        ccd = self.ccd_from(ccd_phase=ccd)
        image_post_cti = cti.add_cti(
            image=image_pre_cti_2d,
            parallel_ccd=ccd,
            parallel_roe=self.roe,
            parallel_traps=trap_list,
            parallel_express=self.express,
            parallel_offset=data.readout_offsets[0],
            parallel_window_start=self.window_start,
            parallel_window_stop=self.window_stop,
            verbosity=self.verbosity,
        )
        return Array1D.manual_native(
            array=image_post_cti.flatten(), pixel_scales=data.pixel_scales
        )


class Clocker2D(AbstractClocker):
    def __init__(
        self,
        iterations=1,
        parallel_roe=ROE(),
        parallel_express=0,
        parallel_charge_injection_mode=False,
        parallel_window_start=0,
        parallel_window_stop=(-1),
        parallel_poisson_traps=False,
        serial_roe=ROE(),
        serial_express=0,
        serial_window_start=0,
        serial_window_stop=(-1),
        verbosity=0,
        poisson_seed=(-1),
    ):
        """
        The CTI Clock for arctic clocking.
        Parameters
        ----------
        iterations
            The number of iterations used to correct CTI from an image.
        parallel_roe
            Contains parameters describing the read-out electronics of the CCD (e.g. CCD dwell times, charge injection
            clocking, etc.) for clocking in the parallel direction.
        parallel_express
            An integer factor describing how parallel pixel-to-pixel transfers are combined into single transfers for
            efficiency (see: https://academic.oup.com/mnras/article/401/1/371/1006825).
        parallel_window_start
            The pixel index of the input image where parallel arCTIc clocking begins, for example
            if `window_start=10` the first 10 pixels are omitted and not clocked.
        parallel_window_start
            The pixel index of the input image where parallel arCTIc clocking ends, for example if `window_start=20`
            any pixels after the 20th pixel are omitted and not clocked.
        verbosity
            Whether to silence print statements and output from the c++ arctic call.
        """
        super().__init__(iterations=iterations, verbosity=verbosity)
        self.parallel_roe = parallel_roe
        self.parallel_express = parallel_express
        self.parallel_charge_injection_mode = parallel_charge_injection_mode
        self.parallel_window_start = parallel_window_start
        self.parallel_window_stop = parallel_window_stop
        self.parallel_poisson_traps = parallel_poisson_traps
        self.serial_roe = serial_roe
        self.serial_express = serial_express
        self.serial_window_start = serial_window_start
        self.serial_window_stop = serial_window_stop
        self.poisson_seed = poisson_seed

    def add_cti(
        self,
        data,
        parallel_ccd=None,
        parallel_trap_list=None,
        serial_ccd=None,
        serial_trap_list=None,
    ):
        if self.parallel_poisson_traps:
            return self.add_cti_poisson_traps(
                data=data,
                parallel_ccd=parallel_ccd,
                parallel_trap_list=parallel_trap_list,
                serial_ccd=serial_ccd,
                serial_trap_list=serial_trap_list,
            )
        if not any([parallel_trap_list, serial_trap_list]):
            raise exc.ClockerException(
                "No Trap species (parallel or serial) were passed to the add_cti method"
            )
        if not any([parallel_ccd, serial_ccd]):
            raise exc.ClockerException(
                "No CCD object(parallel or serial) was passed to the add_cti method"
            )
        parallel_ccd = self.ccd_from(ccd_phase=parallel_ccd)
        serial_ccd = self.ccd_from(ccd_phase=serial_ccd)
        try:
            parallel_offset = data.readout_offsets[0]
            serial_offset = data.readout_offsets[1]
        except AttributeError:
            parallel_offset = 0
            serial_offset = 0
        image_post_cti = cti.add_cti(
            image=data,
            parallel_ccd=parallel_ccd,
            parallel_roe=self.parallel_roe,
            parallel_traps=parallel_trap_list,
            parallel_express=self.parallel_express,
            parallel_offset=parallel_offset,
            parallel_window_start=self.parallel_window_start,
            parallel_window_stop=self.parallel_window_stop,
            serial_ccd=serial_ccd,
            serial_roe=self.serial_roe,
            serial_traps=serial_trap_list,
            serial_express=self.serial_express,
            serial_offset=serial_offset,
            serial_window_start=self.serial_window_start,
            serial_window_stop=self.serial_window_stop,
            verbosity=self.verbosity,
        )
        try:
            return Array2D.manual_mask(array=image_post_cti, mask=data.mask).native
        except AttributeError:
            return image_post_cti

    def remove_cti(
        self,
        data,
        parallel_ccd=None,
        parallel_trap_list=None,
        serial_ccd=None,
        serial_trap_list=None,
    ):
        if not any([parallel_trap_list, serial_trap_list]):
            raise exc.ClockerException(
                "No Trap species (parallel or serial) were passed to the add_cti method"
            )
        if not any([parallel_ccd, serial_ccd]):
            raise exc.ClockerException(
                "No CCD object(parallel or serial) was passed to the add_cti method"
            )
        parallel_ccd = self.ccd_from(ccd_phase=parallel_ccd)
        serial_ccd = self.ccd_from(ccd_phase=serial_ccd)
        image_cti_removed = cti.remove_cti(
            image=data,
            n_iterations=self.iterations,
            parallel_ccd=parallel_ccd,
            parallel_roe=self.parallel_roe,
            parallel_traps=parallel_trap_list,
            parallel_express=self.parallel_express,
            parallel_offset=data.readout_offsets[0],
            parallel_window_start=self.parallel_window_start,
            parallel_window_stop=self.parallel_window_stop,
            serial_ccd=serial_ccd,
            serial_roe=self.serial_roe,
            serial_traps=serial_trap_list,
            serial_express=self.serial_express,
            serial_offset=data.readout_offsets[1],
            serial_window_start=self.serial_window_start,
            serial_window_stop=self.serial_window_stop,
        )
        return Array2D.manual_mask(
            array=image_cti_removed, mask=data.mask, header=data.header
        ).native

    def add_cti_poisson_traps(
        self,
        data,
        parallel_ccd=None,
        parallel_trap_list=None,
        serial_ccd=None,
        serial_trap_list=None,
    ):
        if not any([parallel_trap_list, serial_trap_list]):
            raise exc.ClockerException(
                "No Trap species (parallel or serial) were passed to the add_cti method"
            )
        if not any([parallel_ccd, serial_ccd]):
            raise exc.ClockerException(
                "No CCD object(parallel or serial) was passed to the add_cti method"
            )
        parallel_ccd = self.ccd_from(ccd_phase=parallel_ccd)
        try:
            parallel_offset = data.readout_offsets[0]
        except AttributeError:
            parallel_offset = 0
        image_pre_cti = data.native
        image_post_cti = np.zeros(data.shape_native)
        total_rows = image_post_cti.shape[0]
        total_columns = image_post_cti.shape[1]
        parallel_trap_column_list = []
        for column in range(total_columns):
            parallel_trap_poisson_list = [
                parallel_trap.poisson_density_from(
                    total_pixels=total_rows, seed=self.poisson_seed
                )
                for parallel_trap in parallel_trap_list
            ]
            parallel_trap_column_list.append(parallel_trap_poisson_list)
            image_pre_cti_pass = np.zeros(shape=(total_rows, 1))
            image_pre_cti_pass[:, 0] = image_pre_cti[:, column]
            image_post_cti[:, column] = cti.add_cti(
                image=image_pre_cti_pass,
                parallel_ccd=parallel_ccd,
                parallel_roe=self.parallel_roe,
                parallel_traps=parallel_trap_poisson_list,
                parallel_express=self.parallel_express,
                parallel_offset=parallel_offset,
                parallel_window_start=self.parallel_window_start,
                parallel_window_stop=self.parallel_window_stop,
                verbosity=self.verbosity,
            )[:, 0]
        self.parallel_trap_column_list = parallel_trap_column_list
        serial_ccd = self.ccd_from(ccd_phase=serial_ccd)
        try:
            serial_offset = data.readout_offsets[1]
        except AttributeError:
            serial_offset = 0
        image_post_cti = cti.add_cti(
            image=image_post_cti,
            serial_ccd=serial_ccd,
            serial_roe=self.serial_roe,
            serial_traps=serial_trap_list,
            serial_express=self.serial_express,
            serial_offset=serial_offset,
            serial_window_start=self.serial_window_start,
            serial_window_stop=self.serial_window_stop,
            verbosity=self.verbosity,
        )
        try:
            return Array2D.manual_mask(array=image_post_cti, mask=data.mask).native
        except AttributeError:
            return image_post_cti
