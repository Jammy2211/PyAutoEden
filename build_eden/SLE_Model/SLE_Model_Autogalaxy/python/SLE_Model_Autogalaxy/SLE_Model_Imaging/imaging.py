import numpy as np
import SLE_Model_Autoarray as aa
from SLE_Model_Autogalaxy.SLE_Model_Plane.plane import Plane


class SimulatorImaging(aa.SimulatorImaging):
    def __init__(
        self,
        exposure_time,
        background_sky_level=0.0,
        psf=None,
        normalize_psf=True,
        read_noise=None,
        add_poisson_noise=True,
        noise_if_add_noise_false=0.1,
        noise_seed=(-1),
    ):
        """A class representing a Imaging observation, using the shape of the image, the pixel scale,
        psf, exposure time, etc.

        Parameters
        ----------
        psf : Kernel2D
            An arrays describing the PSF kernel of the image.
        exposure_time
            The exposure time of the simulated imaging.
        background_sky_level
            The level of the background sky of the simulated imaging.
        normalize_psf
            If `True`, the PSF kernel is normalized so all values sum to 1.0.
        read_noise
            The level of read-noise added to the simulated imaging by drawing from a Gaussian distribution with
            sigma equal to the value `read_noise`.
        add_poisson_noise
            Whether Poisson noise corresponding to photon count statistics on the imaging observation is added.
        noise_if_add_noise_false
            If noise is not added to the simulated dataset a `noise_map` must still be returned. This value gives
            the value of noise assigned to every pixel in the noise-map.
        noise_seed
            The random seed used to add random noise, where -1 corresponds to a random seed every run.

        """
        super().__init__(
            psf=psf,
            exposure_time=exposure_time,
            background_sky_level=background_sky_level,
            normalize_psf=normalize_psf,
            read_noise=read_noise,
            add_poisson_noise=add_poisson_noise,
            noise_if_add_noise_false=noise_if_add_noise_false,
            noise_seed=noise_seed,
        )

    def via_plane_from(self, plane, grid):
        """
        Returns a realistic simulated image by applying effects to a plain simulated image.

        Parameters
        ----------
        """
        plane.set_snr_of_snr_light_profiles(
            grid=grid,
            exposure_time=self.exposure_time,
            background_sky_level=self.background_sky_level,
            psf=self.psf,
        )
        image = plane.padded_image_2d_from(
            grid=grid, psf_shape_2d=self.psf.shape_native
        )
        imaging = self.via_image_from(image=image.binned)
        return imaging.trimmed_after_convolution_from(
            kernel_shape=self.psf.shape_native
        )

    def via_galaxies_from(self, galaxies, grid):
        """
        Simulate imaging data for this data, as follows:

        1) Setup the image-plane grid of the Imaging arrays, which defines the coordinates used for the ray-tracing.

        2) Use this grid and the lens and source galaxies to setup a plane, which generates the image of            the simulated imaging data.

        3) Simulate the imaging data, using a special image which ensures edge-effects don't
           degrade simulator of the telescope optics (e.g. the PSF convolution).

        4) Plot the image using Matplotlib, if the plot_imaging bool is True.

        5) Output the dataset to .fits format if a dataset_path and data_name are specified. Otherwise, return the simulated            imaging data instance.
        """
        plane = Plane(
            redshift=float(np.mean([galaxy.redshift for galaxy in galaxies])),
            galaxies=galaxies,
        )
        return self.via_plane_from(plane=plane, grid=grid)