import inspect
import logging
from abc import ABC
from typing import Optional, Dict
from SLE_Model_Autofit.SLE_Model_Mapper.SLE_Model_PriorModel.abstract import (
    AbstractPriorModel,
)
from SLE_Model_Autofit.SLE_Model_NonLinear.SLE_Model_Paths.abstract import AbstractPaths
from SLE_Model_Autofit.SLE_Model_NonLinear.SLE_Model_Samples.summary import (
    SamplesSummary,
)
from SLE_Model_Autofit.SLE_Model_NonLinear.SLE_Model_Samples.pdf import SamplesPDF
from SLE_Model_Autofit.SLE_Model_NonLinear.result import Result
from SLE_Model_Autofit.SLE_Model_NonLinear.SLE_Model_Samples.samples import Samples
from SLE_Model_Autofit.SLE_Model_NonLinear.SLE_Model_Samples.sample import Sample
from SLE_Model_Autofit.SLE_Model_NonLinear.SLE_Model_Analysis.visualize import (
    Visualizer,
)
from SLE_Model_Autofit.SLE_Model_NonLinear.SLE_Model_Samples.util import (
    simple_model_for_kwargs,
)

logger = logging.getLogger(__name__)


class Analysis(ABC):
    """
    Protocol for an analysis. Defines methods that can or
    must be implemented to define a class that compute the
    likelihood that some instance fits some data.
    """

    Result = Result
    Visualizer = Visualizer

    def __getattr__(self, item):
        """
        If a method starts with 'visualize_' then we assume it is associated with
        the Visualizer and forward the call to the visualizer.

        It may be desirable to remove this behaviour as the visualizer component of
        the system becomes more sophisticated.
        """
        if item.startswith("visualize") or item.startswith("should_visualize"):
            _method = getattr(self.Visualizer, item)
        else:
            raise AttributeError(f"Analysis has no attribute {item}")

        def method(*args, **kwargs):
            parameters = inspect.signature(_method).parameters
            if "analyses" in parameters:
                logger.debug(f"Skipping {item} as this is not a combined analysis")
                return
            return _method(self, *args, **kwargs)

        return method

    def compute_latent_samples(self, samples):
        """
        Internal method that manages computation of latent samples from samples.

        Parameters
        ----------
        samples
            The samples from the non-linear search.

        Returns
        -------
        The computed latent samples or None if compute_latent_variable is not implemented.
        """
        try:
            latent_samples = []
            model = samples.model
            for sample in samples.sample_list:
                latent_samples.append(
                    Sample(
                        log_likelihood=sample.log_likelihood,
                        log_prior=sample.log_prior,
                        weight=sample.weight,
                        kwargs=self.compute_latent_variables(
                            sample.instance_for_model(model, ignore_assertions=True)
                        ),
                    )
                )
            return type(samples)(
                sample_list=latent_samples,
                model=simple_model_for_kwargs(latent_samples[0].kwargs),
                samples_info=samples.samples_info,
            )
        except NotImplementedError:
            return None

    def compute_latent_variables(self, instance):
        """
        Override to compute latent variables from the instance.

        Latent variables are expressed as a dictionary:
        {"name": value}

        More complex models can be expressed by separating variables
        names by \'.\'
        {"name.attribute": value}

        Parameters
        ----------
        instance
            An instance of the model.

        Returns
        -------
        The computed latent variables.
        """
        raise NotImplementedError()

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

    def log_likelihood_function(self, instance):
        raise NotImplementedError()

    def save_attributes(self, paths):
        pass

    def save_results(self, paths, result):
        pass

    def save_results_combined(self, paths, result):
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

    def make_result(
        self, samples_summary, paths, samples=None, search_internal=None, analysis=None
    ):
        """
        Returns the `Result` of the non-linear search after it is completed.

        The result type is defined as a class variable in the `Analysis` class. It can be manually overwritten
        by a user to return a user-defined result object, which can be extended with additional methods and attributes
        specific to the model-fit.

        The standard `Result` object may include:

        - The samples summary, which contains the maximum log likelihood instance and median PDF model.

        - The paths of the search, which are used for loading the samples and search internal below when a search
        is resumed.

        - The samples of the non-linear search (e.g. MCMC chains) also stored in `samples.csv`.

        - The non-linear search used for the fit in its internal representation, which is used for resuming a search
        and making bespoke visualization using the search's internal results.

        - The analysis used to fit the model (default disabled to save memory, but option may be useful for certain
        projects).

        Parameters
        ----------
        samples_summary
            The summary of the samples of the non-linear search, which include the maximum log likelihood instance and
            median PDF model.
        paths
            An object describing the paths for saving data (e.g. hard-disk directories or entries in sqlite database).
        samples
            The samples of the non-linear search, for example the chains of an MCMC run.
        search_internal
            The internal representation of the non-linear search used to perform the model-fit.
        analysis
            The analysis used to fit the model.

        Returns
        -------
        Result
            The result of the non-linear search, which is defined as a class variable in the `Analysis` class.
        """
        return self.Result(
            samples_summary=samples_summary,
            paths=paths,
            samples=samples,
            search_internal=search_internal,
            analysis=analysis,
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
