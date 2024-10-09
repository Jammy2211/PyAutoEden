import logging
from typing import Tuple
from SLE_Model_Autofit.SLE_Model_Mapper.SLE_Model_Prior.abstract import Prior
from SLE_Model_Autofit.SLE_Model_Mapper.SLE_Model_Prior.tuple_prior import TuplePrior
from SLE_Model_Autofit.SLE_Model_Mapper.SLE_Model_PriorModel.abstract import (
    AbstractPriorModel,
)
from SLE_Model_Autofit.SLE_Model_Mapper.SLE_Model_PriorModel.collection import (
    Collection,
)
from SLE_Model_Autofit.SLE_Model_NonLinear.SLE_Model_Analysis.analysis import Analysis
from SLE_Model_Autofit.SLE_Model_NonLinear.SLE_Model_Analysis.indexed import (
    IndexCollectionAnalysis,
)
from SLE_Model_Autofit.SLE_Model_NonLinear.SLE_Model_Paths.abstract import AbstractPaths

logger = logging.getLogger(__name__)


class FreeParameterAnalysis(IndexCollectionAnalysis):
    def __init__(self, *analyses: Analysis, free_parameters: Tuple[(Prior, ...)]):
        """
        A combined analysis with free parameters.

        All parameters for the model are shared across every analysis except
        for the free parameters which are allowed to vary for individual
        analyses.

        Parameters
        ----------
        analyses
            A list of analyses
        free_parameters
            A list of priors which are independent for each analysis
        """
        super().__init__(*analyses)
        self.free_parameters = [
            parameter for parameter in free_parameters if isinstance(parameter, Prior)
        ]
        self.free_parameters += [
            prior
            for parameter in free_parameters
            if isinstance(parameter, (AbstractPriorModel, TuplePrior))
            for prior in parameter.priors
        ]

    def modify_model(self, model):
        """
        Create prior models where free parameters are replaced with new
        priors. Return those prior models as a collection.

        The number of dimensions of the new prior model is the number of the
        old one plus the number of free parameters multiplied by the number
        of free parameters.

        Parameters
        ----------
        model
            The original model

        Returns
        -------
        A new model with all the same priors except for those associated
        with free parameters.
        """
        return Collection(
            [
                analysis.modify_model(
                    model.mapper_from_partial_prior_arguments(
                        {
                            free_parameter: free_parameter.new()
                            for free_parameter in self.free_parameters
                        }
                    )
                )
                for analysis in self.analyses
            ]
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
        return FreeParameterAnalysis(
            *(
                analysis.modify_before_fit(paths, model_)
                for (analysis, model_) in zip(self.analyses, model)
            ),
            free_parameters=tuple(self.free_parameters)
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
        return FreeParameterAnalysis(
            *(
                analysis.modify_after_fit(paths, model, result)
                for (analysis, model_) in zip(self.analyses, model)
            ),
            free_parameters=tuple(self.free_parameters)
        )
