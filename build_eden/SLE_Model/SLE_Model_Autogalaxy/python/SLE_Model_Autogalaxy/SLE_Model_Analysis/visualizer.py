import os
from os import path
from typing import Dict, List, Union
from SLE_Model_Autoconf import conf
import SLE_Model_Autoarray as aa
import SLE_Model_Autoarray.SLE_Model_Plot as aplt
from SLE_Model_Autogalaxy.SLE_Model_Galaxy.galaxy import Galaxy
from SLE_Model_Autogalaxy.SLE_Model_Galaxy.SLE_Model_Plot.galaxy_plotters import (
    GalaxyPlotter,
)
from SLE_Model_Autogalaxy.SLE_Model_Galaxy.SLE_Model_Plot.adapt_plotters import (
    AdaptPlotter,
)
from SLE_Model_Autogalaxy.SLE_Model_Plane.plane import Plane
from SLE_Model_Autogalaxy.SLE_Model_Plane.SLE_Model_Plot.plane_plotters import (
    PlanePlotter,
)
from SLE_Model_Autogalaxy.SLE_Model_Plot.SLE_Model_Include.two_d import Include2D
from SLE_Model_Autogalaxy.SLE_Model_Plot.SLE_Model_MatPlot.one_d import MatPlot1D
from SLE_Model_Autogalaxy.SLE_Model_Plot.SLE_Model_MatPlot.two_d import MatPlot2D


def setting(section, name):
    if isinstance(section, str):
        return conf.instance["visualize"]["plots"][section][name]
    for sect in reversed(section):
        try:
            return conf.instance["visualize"]["plots"][sect][name]
        except KeyError:
            continue
    return conf.instance["visualize"]["plots"][section[0]][name]


def plot_setting(section, name):
    return setting(section, name)


class Visualizer:
    def __init__(self, visualize_path):
        """
        Visualizes a model-fit, including components of the model and fit objects.

        The `Visualizer` is typically used in the `Analysis` class of a non-linear search to visualize the maximum
        log likelihood model of the model-fit so far.

        The methods of the `Visualizer` are called throughout a non-linear search using the `Analysis`
        classes `visualize` method.

        The images output by the `Visualizer` are customized using the file `config/visualize/plots.ini`.

        Parameters
        ----------
        visualize_path
            The path on the hard-disk to the `image` folder of the non-linear searches results.
        """
        self.visualize_path = visualize_path
        self.include_2d = Include2D()
        try:
            os.makedirs(visualize_path)
        except FileExistsError:
            pass

    def mat_plot_1d_from(self, subfolders, format="png"):
        """
        Returns a 1D matplotlib plotting object whose `Output` class uses the `visualizer_path`, such that it outputs
        images to the `image` folder of the non-linear search.

        Parameters
        ----------
        subfolders
            Subfolders between the `image` folder of the non-linear search and where the images are output. For example,
            images associsted with a fit are output to the subfolder `fit`.
        format
            The format images are output as, e.g. `.png` files.

        Returns
        -------
        MatPlot1D
            The 1D matplotlib plotter object.
        """
        return MatPlot1D(
            output=aplt.Output(
                path=path.join(self.visualize_path, subfolders), format=format
            )
        )

    def mat_plot_2d_from(self, subfolders, format="png"):
        """
        Returns a 2D matplotlib plotting object whose `Output` class uses the `visualizer_path`, such that it outputs
        images to the `image` folder of the non-linear search.

        Parameters
        ----------
        subfolders
            Subfolders between the `image` folder of the non-linear search and where the images are output. For example,
            images associsted with a fit are output to the subfolder `fit`.
        format
            The format images are output as, e.g. `.png` files.

        Returns
        -------
        MatPlot2D
            The 2D matplotlib plotter object.
        """
        return MatPlot2D(
            output=aplt.Output(
                path=path.join(self.visualize_path, subfolders), format=format
            )
        )

    def visualize_imaging(self, imaging):
        """
        Visualizes an `Imaging` dataset object.

        Images are output to the `image` folder of the `visualize_path` in a subfolder called `imaging`. When used with
        a non-linear search the `visualize_path` points to the search's results folder.
        `.
        Visualization includes individual images of attributes of the dataset (e.g. the image, noise map, PSF) and a
        subplot of all these attributes on the same figure.

        The images output by the `Visualizer` are customized using the file `config/visualize/plots.ini` under the
        [dataset] header.

        Parameters
        ----------
        imaging
            The imaging dataset whose attributes are visualized.
        """

        def should_plot(name):
            return plot_setting(section=["dataset", "imaging"], name=name)

        mat_plot_2d = self.mat_plot_2d_from(subfolders="dataset")
        imaging_plotter = aplt.ImagingPlotter(
            imaging=imaging, mat_plot_2d=mat_plot_2d, include_2d=self.include_2d
        )
        imaging_plotter.figures_2d(
            data=should_plot("data"),
            noise_map=should_plot("noise_map"),
            psf=should_plot("psf"),
            signal_to_noise_map=should_plot("signal_to_noise_map"),
        )
        if should_plot("subplot_dataset"):
            imaging_plotter.subplot_dataset()

    def visualize_interferometer(self, interferometer):
        """
        Visualizes an `Interferometer` dataset object.

        Images are output to the `image` folder of the `visualize_path` in a subfolder called `interferometer`. When
        used with a non-linear search the `visualize_path` points to the search's results folder.

        Visualization includes individual images of attributes of the dataset (e.g. the visibilities, noise map,
        uv-wavelengths) and a subplot of all these attributes on the same figure.

        The images output by the `Visualizer` are customized using the file `config/visualize/plots.ini` under the
        [dataset] header.

        Parameters
        ----------
        interferometer
            The interferometer dataset whose attributes are visualized.
        """

        def should_plot(name):
            return plot_setting(section=["dataset", "interferometer"], name=name)

        mat_plot_2d = self.mat_plot_2d_from(subfolders="dataset")
        interferometer_plotter = aplt.InterferometerPlotter(
            dataset=interferometer, include_2d=self.include_2d, mat_plot_2d=mat_plot_2d
        )
        if should_plot("subplot_dataset"):
            interferometer_plotter.subplot_dataset()
        interferometer_plotter.figures_2d(
            data=should_plot("data"),
            u_wavelengths=should_plot("uv_wavelengths"),
            v_wavelengths=should_plot("uv_wavelengths"),
            amplitudes_vs_uv_distances=should_plot("amplitudes_vs_uv_distances"),
            phases_vs_uv_distances=should_plot("phases_vs_uv_distances"),
            dirty_image=should_plot("dirty_image"),
            dirty_noise_map=should_plot("dirty_noise_map"),
            dirty_signal_to_noise_map=should_plot("dirty_signal_to_noise_map"),
        )

    def visualize_plane(self, plane, grid, during_analysis):
        """
        Visualizes a `Plane` object.

        Images are output to the `image` folder of the `visualize_path` in a subfolder called `plane`. When
        used with a non-linear search the `visualize_path` points to the search's results folder and this function
        visualizes the maximum log likelihood `Plane` inferred by the search so far.

        Visualization includes individual images of attributes of the plane (e.g. its image, convergence, deflection
        angles) and a subplot of all these attributes on the same figure.

        The images output by the `Visualizer` are customized using the file `config/visualize/plots.ini` under the
        [plane] header.

        Parameters
        ----------
        plane
            The maximum log likelihood `Plane` of the non-linear search.
        grid
            A 2D grid of (y,x) arc-second coordinates used to perform ray-tracing, which is the masked grid tied to
            the dataset.
        during_analysis
            Whether visualization is performed during a non-linear search or once it is completed.
        """

        def should_plot(name):
            return plot_setting(section="plane", name=name)

        subfolders = "plane"
        mat_plot_2d = self.mat_plot_2d_from(subfolders=subfolders)
        plane_plotter = PlanePlotter(
            plane=plane, grid=grid, mat_plot_2d=mat_plot_2d, include_2d=self.include_2d
        )
        if should_plot("subplot_plane"):
            plane_plotter.subplot()
        if should_plot("subplot_galaxy_images"):
            plane_plotter.subplot_galaxy_images()
        plane_plotter.figures_2d(
            image=should_plot("image"),
            convergence=should_plot("convergence"),
            potential=should_plot("potential"),
            deflections_y=should_plot("deflections"),
            deflections_x=should_plot("deflections"),
            magnification=should_plot("magnification"),
        )
        if (not during_analysis) and should_plot("all_at_end_png"):
            mat_plot_2d = self.mat_plot_2d_from(subfolders=path.join(subfolders, "end"))
            plane_plotter = PlanePlotter(
                plane=plane,
                grid=grid,
                mat_plot_2d=mat_plot_2d,
                include_2d=self.include_2d,
            )
            plane_plotter.figures_2d(
                image=True,
                convergence=True,
                potential=True,
                deflections_y=True,
                deflections_x=True,
                magnification=True,
            )
        if (not during_analysis) and should_plot("all_at_end_fits"):
            mat_plot_2d = self.mat_plot_2d_from(
                subfolders=path.join(subfolders, "fits"), format="fits"
            )
            plane_plotter = PlanePlotter(
                plane=plane,
                grid=grid,
                mat_plot_2d=mat_plot_2d,
                include_2d=self.include_2d,
            )
            plane_plotter.figures_2d(
                image=True,
                convergence=True,
                potential=True,
                deflections_y=True,
                deflections_x=True,
                magnification=True,
            )

    def visualize_galaxies(self, galaxies, grid, during_analysis):
        """
        Visualizes a list of `Galaxy` objects.

        Images are output to the `image` folder of the `visualize_path` in a subfolder called `galaxies`. When
        used with a non-linear search the `visualize_path` points to the search's results folder and this function
        visualizes the maximum log likelihood `Galaxy`'s inferred by the search so far.

        Visualization includes individual images of attributes of each galaxy (e.g. 1D plots of their image,
        convergence) and a subplot of all these attributes on the same figure.

        The images output by the `Visualizer` are customized using the file `config/visualize/plots.ini` under the
        [galaxies] header.

        Parameters
        ----------
        galaxies
            A list of the maximum log likelihood `Galaxy`'s of the non-linear search.
        grid
            A 2D grid of (y,x) arc-second coordinates used to perform ray-tracing, which is the masked grid tied to
            the dataset.
        during_analysis
            Whether visualization is performed during a non-linear search or once it is completed.
        """

        def should_plot(name):
            return plot_setting(section="galaxies", name=name)

        mat_plot_1d = self.mat_plot_1d_from(subfolders="galaxies")
        for galaxy in galaxies:
            galaxy_plotter = GalaxyPlotter(
                galaxy=galaxy,
                grid=grid,
                mat_plot_1d=mat_plot_1d,
                include_2d=self.include_2d,
            )
            try:
                galaxy_plotter.figures_1d_decomposed(
                    image=should_plot("image"),
                    convergence=should_plot("convergence"),
                    potential=should_plot("potential"),
                )
            except OverflowError:
                pass

    def visualize_inversion(self, inversion, during_analysis):
        """
        Visualizes an `Inversion` object.

        Images are output to the `image` folder of the `visualize_path` in a subfolder called `inversion`. When
        used with a non-linear search the `visualize_path` points to the search's results folder and this function
        visualizes the maximum log likelihood `Inversion` inferred by the search so far.

        Visualization includes individual images of attributes of the dataset (e.g. the reconstructed image, the
        reconstruction) and a subplot of all these attributes on the same figure.

        The images output by the `Visualizer` are customized using the file `config/visualize/plots.ini` under the
        [inversion] header.

        Parameters
        ----------
        inversion
            The inversion used to fit the dataset whose attributes are visualized.
        during_analysis
            Whether visualization is performed during a non-linear search or once it is completed.
        """

        def should_plot(name):
            return plot_setting(section="inversion", name=name)

        subfolders = "inversion"
        mat_plot_2d = self.mat_plot_2d_from(subfolders=subfolders)
        inversion_plotter = aplt.InversionPlotter(
            inversion=inversion, mat_plot_2d=mat_plot_2d, include_2d=self.include_2d
        )
        inversion_plotter.figures_2d(
            reconstructed_image=should_plot("reconstructed_image")
        )
        inversion_plotter.figures_2d_of_pixelization(
            pixelization_index=0,
            reconstructed_image=should_plot("reconstructed_image"),
            reconstruction=should_plot("reconstruction"),
            errors=should_plot("errors"),
            regularization_weights=should_plot("regularization_weights"),
        )
        if should_plot("subplot_inversion"):
            mapper_list = inversion.cls_list_from(cls=aa.AbstractMapper)
            for mapper_index in range(len(mapper_list)):
                inversion_plotter.subplot_of_mapper(mapper_index=mapper_index)
        if (not during_analysis) and should_plot("all_at_end_png"):
            mat_plot_2d = self.mat_plot_2d_from(subfolders=path.join(subfolders, "end"))
            inversion_plotter = aplt.InversionPlotter(
                inversion=inversion, mat_plot_2d=mat_plot_2d, include_2d=self.include_2d
            )
            inversion_plotter.figures_2d(reconstructed_image=True)
            inversion_plotter.figures_2d_of_pixelization(
                pixelization_index=0,
                reconstructed_image=True,
                reconstruction=True,
                errors=True,
                regularization_weights=True,
            )
        if (not during_analysis) and should_plot("all_at_end_fits"):
            mat_plot_2d = self.mat_plot_2d_from(
                subfolders=path.join(subfolders, "fits"), format="fits"
            )
            inversion_plotter = aplt.InversionPlotter(
                inversion=inversion, mat_plot_2d=mat_plot_2d, include_2d=self.include_2d
            )
            inversion_plotter.figures_2d(reconstructed_image=True)
            inversion_plotter.figures_2d_of_pixelization(
                pixelization_index=0,
                reconstructed_image=True,
                reconstruction=True,
                errors=True,
                regularization_weights=True,
                interpolate_to_uniform=True,
            )

    def visualize_adapt_images(self, adapt_galaxy_image_path_dict, adapt_model_image):
        """
        Visualizes the hyper-images and hyper dataset inferred by a model-fit.

        Images are output to the `image` folder of the `visualize_path` in a subfolder called `hyper`. When
        used with a non-linear search the `visualize_path` points to the search's results folder.

        Visualization includes individual images of attributes of the hyper dataset (e.g. the adapt image) and
        a subplot of all galaxy images on the same figure.

        The images output by the `Visualizer` are customized using the file `config/visualize/plots.ini` under the
        [hyper] header.

        Parameters
        ----------
        adapt_galaxy_image_path_dict
            A dictionary mapping the path to each galaxy (e.g. its name) to its corresponding galaxy image.
        adapt_model_image
            The adapt image which corresponds to the sum of galaxy images.
        """

        def should_plot(name):
            return plot_setting(section="adapt", name=name)

        mat_plot_2d = self.mat_plot_2d_from(subfolders="adapt")
        hyper_plotter = AdaptPlotter(
            mat_plot_2d=mat_plot_2d, include_2d=self.include_2d
        )
        if should_plot("model_image"):
            hyper_plotter.figure_adapt_model_image(adapt_model_image=adapt_model_image)
        if should_plot("images_of_galaxies"):
            hyper_plotter.subplot_adapt_images_of_galaxies(
                adapt_galaxy_image_path_dict=adapt_galaxy_image_path_dict
            )

    def visualize_contribution_maps(self, plane):
        """
        Visualizes the contribution maps that are used for hyper features which adapt a model to the dataset it is
        fitting.

        Images are output to the `image` folder of the `visualize_path` in a subfolder called `hyper`. When
        used with a non-linear search the `visualize_path` points to the search's results folder and this function
        visualizes the maximum log likelihood contribution maps inferred by the search so far.

        Visualization includes individual images of attributes of the hyper dataset (e.g. the contribution map of
        each galaxy) and a subplot of all contribution maps on the same figure.

        The images output by the `Visualizer` are customized using the file `config/visualize/plots.ini` under the
        [hyper] header.

        Parameters
        ----------
        plane
            The maximum log likelihood `Plane` of the non-linear search which is used to plot the contribution maps.
        """

        def should_plot(name):
            return plot_setting(section="adapt", name=name)

        mat_plot_2d = self.mat_plot_2d_from(subfolders="adapt")
        hyper_plotter = AdaptPlotter(
            mat_plot_2d=mat_plot_2d, include_2d=self.include_2d
        )
        if hasattr(plane, "contribution_map_list"):
            if should_plot("contribution_map_list"):
                hyper_plotter.subplot_contribution_map_list(
                    contribution_map_list_list=plane.contribution_map_list
                )