import logging
from abc import ABC
import os
from SLE_Model_Autoconf import conf
from SLE_Model_Autofit.SLE_Model_Mapper.SLE_Model_PriorModel.abstract import (
    AbstractPriorModel,
)
from SLE_Model_Autofit.SLE_Model_NonLinear.SLE_Model_Paths.abstract import AbstractPaths
from SLE_Model_Autofit.SLE_Model_NonLinear.result import Result

logger = logging.getLogger(__name__)


class Analysis(ABC):
    """
    Protocol for an analysis. Defines methods that can or
    must be implemented to define a class that compute the
    likelihood that some instance fits some data.
    """

    def with_model(self, model):
        """
        Associate an explicit model with this analysis. Instances of the model
        will be used to compute log likelihood in place of the model passed
        from the search.

        Parameters
        ----------
        model
            A model to associate with this analysis

        Returns
        -------
        An analysis for that model
        """
        from SLE_Model_Autofit.SLE_Model_NonLinear.SLE_Model_Analysis.model_analysis import (
            ModelAnalysis,
        )

        return ModelAnalysis(analysis=self, model=model)

    def should_visualize(self, paths):
        """
        Whether a visualize method should continue and perform visualization, or be terminated early.

        If a model-fit has already completed, the default behaviour is for visualization to be bypassed in order
        to make model-fits run faster. However, visualization can be forced to run via
        the `force_visualization_overwrite`, for example if a user wants to plot additional images that were not
        output on the original run.

        PyAutoFit test mode also disables visualization, irrespective of the `force_visualization_overwite`
        config input.

        Parameters
        ----------
        paths
            The PyAutoFit paths object which manages all paths, e.g. where the non-linear search outputs are stored,
            visualization and the pickled objects used by the aggregator output by this function.


        Returns
        -------
        A bool determining whether visualization should be performed or not.
        """
        if os.environ.get("PYAUTOFIT_TEST_MODE") == "1":
            return False
        return (not paths.is_complete) or conf.instance["general"]["output"][
            "force_visualize_overwrite"
        ]

    def log_likelihood_function(self, instance):
        raise NotImplementedError()

    def visualize_before_fit(self, paths, model):
        pass

    def visualize(self, paths, instance, during_analysis):
        pass

    def visualize_before_fit_combined(self, analyses, paths, model):
        pass

    def visualize_combined(self, analyses, paths, instance, during_analysis):
        pass

    def save_attributes_for_aggregator(self, paths):
        pass

    def save_results_for_aggregator(self, paths, result):
        pass

    def modify_before_fit(self, paths, model):
        """
        Overwrite this method to modify the attributes of the `Analysis` class before the non-linear search begins.

        An example use-case is using properties of the model to alter the `Analysis` class in ways that can speed up
        the fitting performed in the `log_likelihood_function`.
        """
        return self

    def modify_model(self, model):
        return model

    def modify_after_fit(self, paths, model, result):
        """
        Overwrite this method to modify the attributes of the `Analysis` class before the non-linear search begins.

        An example use-case is using properties of the model to alter the `Analysis` class in ways that can speed up
        the fitting performed in the `log_likelihood_function`.
        """
        return self

    def make_result(self, samples, model, sigma=1.0, use_errors=True, use_widths=False):
        return Result(
            samples=samples,
            model=model,
            sigma=sigma,
            use_errors=use_errors,
            use_widths=use_widths,
        )

    def profile_log_likelihood_function(self, paths, instance):
        """
        Overwrite this function for profiling of the log likelihood function to be performed every update of a
        non-linear search.

        This behaves analogously to overwriting the `visualize` function of the `Analysis` class, whereby the user
        fills in the project-specific behaviour of the profiling.

        Parameters
        ----------
        paths
            An object describing the paths for saving data (e.g. hard-disk directories or entries in sqlite database).
        instance
            The maximum likliehood instance of the model so far in the non-linear search.
        """
        pass

    def __add__(self, other):
        """
        Analyses can be added together. The resultant
        log likelihood function returns the sum of the
        underlying log likelihood functions.

        Parameters
        ----------
        other
            Another analysis class

        Returns
        -------
        A class that computes log likelihood based on both analyses
        """
        from SLE_Model_Autofit.SLE_Model_NonLinear.SLE_Model_Analysis.combined import (
            CombinedAnalysis,
        )

        if isinstance(other, CombinedAnalysis):
            return other + self
        return CombinedAnalysis(self, other)

    def __radd__(self, other):
        """
        Allows analysis to be used in sum
        """
        if other == 0:
            return self
        return self + other
