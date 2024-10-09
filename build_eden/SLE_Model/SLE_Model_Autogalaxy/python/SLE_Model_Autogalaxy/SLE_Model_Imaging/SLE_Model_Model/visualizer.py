import SLE_Model_Autofit as af
from SLE_Model_Autoarray import exc
from SLE_Model_Autogalaxy.SLE_Model_Imaging.SLE_Model_Model.plotter_interface import (
    PlotterInterfaceImaging,
)


class VisualizerImaging(af.Visualizer):
    @staticmethod
    def visualize_before_fit(analysis, paths, model):
        """
        PyAutoFit calls this function immediately before the non-linear search begins.

        It visualizes objects which do not change throughout the model fit like the dataset.

        Parameters
        ----------
        paths
            The paths object which manages all paths, e.g. where the non-linear search outputs are stored,
            visualization and the pickled objects used by the aggregator output by this function.
        model
            The model object, which includes model components representing the galaxies that are fitted to
            the imaging data.
        """
        plotter = PlotterInterfaceImaging(
            image_path=paths.image_path, title_prefix=analysis.title_prefix
        )
        plotter.imaging(dataset=analysis.dataset)
        if analysis.adapt_images is not None:
            plotter.adapt_images(adapt_images=analysis.adapt_images)

    @staticmethod
    def visualize(analysis, paths, instance, during_analysis):
        """
        Output images of the maximum log likelihood model inferred by the model-fit. This function is called throughout
        the non-linear search at regular intervals, and therefore provides on-the-fly visualization of how well the
        model-fit is going.

        The visualization performed by this function includes:

        - Images of the best-fit galaxies, including the images of each of its galaxies.

        - Images of the best-fit `FitImaging`, including the model-image, residuals and chi-squared of its fit to
          the imaging data.

        - The adapt-images of the model-fit showing how the galaxies are used to represent different galaxies in
          the dataset.

        The images output by this function are customized using the file `config/visualize/plots.yaml`.

        Parameters
        ----------
        paths
            The paths object which manages all paths, e.g. where the non-linear search outputs are stored,
            visualization, and the pickled objects used by the aggregator output by this function.
        instance
            An instance of the model that is being fitted to the data by this analysis (whose parameters have been set
            via a non-linear search).
        during_analysis
            If True the visualization is being performed midway through the non-linear search before it is finished,
            which may change which images are output.
        """
        fit = analysis.fit_from(instance=instance)
        plotter = PlotterInterfaceImaging(
            image_path=paths.image_path, title_prefix=analysis.title_prefix
        )
        plotter.imaging(dataset=analysis.dataset)
        try:
            plotter.fit_imaging(fit=fit, during_analysis=during_analysis)
        except exc.InversionException:
            pass
        galaxies = fit.galaxies_linear_light_profiles_to_light_profiles
        plotter.galaxies(
            galaxies=galaxies, grid=fit.grids.uniform, during_analysis=during_analysis
        )
        plotter.galaxies_1d(
            galaxies=galaxies, grid=fit.grids.uniform, during_analysis=during_analysis
        )
        if fit.inversion is not None:
            plotter.inversion(inversion=fit.inversion, during_analysis=during_analysis)

    @staticmethod
    def visualize_before_fit_combined(analyses, paths, model):
        """
        Performs visualization before the non-linear search begins of information which shared across all analyses
        on a single matplotlib figure.

        This function outputs visuals of all information which does not vary during the fit, for example the dataset
        being fitted.

        Parameters
        ----------
        analyses
            The list of all analysis objects used for fitting via yhe non-linear search.
        paths
            The paths object which manages all paths, e.g. where the non-linear search outputs are stored,
            visualization and the pickled objects used by the aggregator output by this function.
        model
            The model object, which includes model components representing the galaxies that are fitted to
            the imaging data.
        """
        if analyses is None:
            return
        plotter = PlotterInterfaceImaging(
            image_path=paths.image_path, title_prefix=analyses[0].title_prefix
        )
        dataset_list = [analysis.dataset for analysis in analyses]
        plotter.imaging_combined(dataset_list=dataset_list)

    @staticmethod
    def visualize_combined(analyses, paths, instance, during_analysis):
        """
        Performs visualization during the non-linear search of information which is shared across all analyses on a
        single matplotlib figure.

        This function outputs visuals of all information which varies during the fit, for example the model-fit to
        the dataset being fitted.

        Parameters
        ----------
        analyses
            The list of all analysis objects used for fitting via yhe non-linear search.
        paths
            The paths object which manages all paths, e.g. where the non-linear search outputs are stored,
            visualization and the pickled objects used by the aggregator output by this function.
        model
            The model object, which includes model components representing the galaxies that are fitted to
            the imaging data.
        """
        if analyses is None:
            return
        plotter = PlotterInterfaceImaging(
            image_path=paths.image_path, title_prefix=analyses[0].title_prefix
        )
        fit_list = [analysis.fit_from(instance=instance) for analysis in analyses]
        plotter.fit_imaging_combined(fit_list=fit_list)
