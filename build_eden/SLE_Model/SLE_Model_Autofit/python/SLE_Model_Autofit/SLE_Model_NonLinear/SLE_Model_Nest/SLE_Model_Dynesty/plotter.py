from dynesty import plotting as dyplot

from VIS_CTI_Autofit.VIS_CTI_Plot import SamplesPlotter
from VIS_CTI_Autofit.VIS_CTI_Plot.samples_plotters import skip_plot_in_test_mode


class DynestyPlotter(SamplesPlotter):
    @skip_plot_in_test_mode
    def boundplot(self, **kwargs):

        dyplot.boundplot(
            results=self.samples.results_internal,
            labels=self.model.parameter_labels_with_superscripts,
            **kwargs
        )

        self.output.to_figure(structure=None, auto_filename="boundplot")
        self.close()

    @skip_plot_in_test_mode
    def cornerbound(self, **kwargs):

        dyplot.cornerbound(
            results=self.samples.results_internal,
            labels=self.model.parameter_labels_with_superscripts,
            **kwargs
        )

        self.output.to_figure(structure=None, auto_filename="cornerbound")
        self.close()

    @skip_plot_in_test_mode
    def cornerplot(self, **kwargs):

        dyplot.cornerplot(
            results=self.samples.results_internal,
            labels=self.model.parameter_labels_with_superscripts,
            **kwargs
        )

        self.output.to_figure(structure=None, auto_filename="cornerplot")
        self.close()

    @skip_plot_in_test_mode
    def cornerpoints(self, **kwargs):

        try:
            dyplot.cornerpoints(
                results=self.samples.results_internal,
                labels=self.model.parameter_labels_with_superscripts,
                **kwargs
            )

            self.output.to_figure(structure=None, auto_filename="cornerpoints")
        except ValueError:
            pass

        self.close()

    @skip_plot_in_test_mode
    def runplot(self, **kwargs):

        try:
            dyplot.runplot(results=self.samples.results_internal, **kwargs)
        except ValueError:
            pass

        self.output.to_figure(structure=None, auto_filename="runplot")
        self.close()

    @skip_plot_in_test_mode
    def traceplot(self, **kwargs):

        dyplot.traceplot(results=self.samples.results_internal, **kwargs)

        self.output.to_figure(structure=None, auto_filename="traceplot")
        self.close()
