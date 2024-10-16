import logging
from typing import Optional
from SLE_Model_Autofit.SLE_Model_NonLinear.SLE_Model_Analysis.analysis import Analysis
from SLE_Model_Autofit.SLE_Model_NonLinear.SLE_Model_Analysis.combined import (
    CombinedAnalysis,
    CombinedResult,
)
from SLE_Model_Autofit.SLE_Model_NonLinear.SLE_Model_Paths.abstract import AbstractPaths
from SLE_Model_Autofit.SLE_Model_NonLinear.SLE_Model_Paths.abstract import AbstractPaths
from SLE_Model_Autofit.SLE_Model_NonLinear.SLE_Model_Samples.summary import (
    SamplesSummary,
)
from SLE_Model_Autofit.SLE_Model_Mapper.SLE_Model_PriorModel.collection import (
    Collection,
)
from SLE_Model_Autofit.SLE_Model_NonLinear.SLE_Model_Samples import SamplesPDF

logger = logging.getLogger(__name__)


class IndexedAnalysis:
    def __init__(self, analysis, index):
        """
        One instance in a collection corresponds to this analysis. That
        instance is identified by its index in the collection.

        Parameters
        ----------
        analysis
            An analysis that can be applied to an instance in a collection
        index
            The index of the instance that should be passed to the analysis
        """
        if isinstance(analysis, IndexedAnalysis):
            analysis = analysis.analysis
        self.analysis = analysis
        self.index = index

    def log_likelihood_function(self, instance):
        """
        Compute the log likelihood by taking the instance at the index
        """
        return self.analysis.log_likelihood_function(instance[self.index])

    def visualize(self, paths, instance, during_analysis):
        return self.analysis.visualize(paths, instance[self.index], during_analysis)

    def visualize_combined(self, analyses, paths, instance, during_analysis):
        return self.analysis.visualize_combined(
            analyses, paths, instance[self.index], during_analysis
        )

    def profile_log_likelihood_function(self, paths, instance):
        return self.profile_log_likelihood_function(paths, instance[self.index])

    def __getattr__(self, item):
        if item in ("__getstate__", "__setstate__"):
            raise AttributeError(item)
        return getattr(self.analysis, item)

    def make_result(
        self, samples_summary, paths, samples=None, search_internal=None, analysis=None
    ):
        return self.analysis.make_result(
            samples_summary, paths, samples, search_internal, analysis
        )


class IndexCollectionAnalysis(CombinedAnalysis):
    def __init__(self, *analyses):
        """
        Collection of analyses where each analysis has a different
        corresponding model.

        Parameters
        ----------
        analyses
            A list of analyses each with a separate model
        """
        super().__init__(
            *[
                IndexedAnalysis(analysis, index)
                for (index, analysis) in enumerate(analyses)
            ]
        )

    def make_result(
        self, samples_summary, paths, samples=None, search_internal=None, analysis=None
    ):
        """
        Associate each model with an analysis when creating the result.
        """
        child_results = [
            analysis.make_result(
                (
                    samples_summary.subsamples(model)
                    if (samples_summary is not None)
                    else None
                ),
                paths,
                (samples.subsamples(model) if (samples is not None) else None),
                search_internal,
                analysis,
            )
            for (model, analysis) in zip(samples_summary.model, self.analyses)
        ]
        return CombinedResult(
            child_results, samples=samples, samples_summary=samples_summary
        )

    def modify_before_fit(self, paths, model):
        """
        Modify the analysis before fitting.

        Parameters
        ----------
        paths
            An object describing the paths for saving data (e.g. hard-disk directories or entries in sqlite database).
        model
            The model which is to be fitted.
        """
        return CombinedAnalysis(
            *(analysis.modify_before_fit(paths, model) for analysis in self.analyses)
        )

    def modify_after_fit(self, paths, model, result):
        """
        Modify the analysis after fitting.

        Parameters
        ----------
        paths
            An object describing the paths for saving data (e.g. hard-disk directories or entries in sqlite database).
        model
            The model which is to be fitted.
        result
            The result of the fit.
        """
        return CombinedAnalysis(
            *(
                analysis.modify_after_fit(paths, model, result)
                for analysis in self.analyses
            )
        )
