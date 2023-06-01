from abc import ABC
from typing import Optional
from SLE_Model_Autofit.SLE_Model_Graphical.SLE_Model_ExpectationPropagation import (
    AbstractFactorOptimiser,
)
from SLE_Model_Autofit.SLE_Model_Graphical.SLE_Model_FactorGraphs.factor import FactorKW
from SLE_Model_Autofit.SLE_Model_Mapper.SLE_Model_PriorModel.prior_model import (
    AbstractPriorModel,
)
from SLE_Model_Autofit.SLE_Model_Text.formatter import TextFormatter
from SLE_Model_Autofit.SLE_Model_Tools.namer import namer
from SLE_Model_Autofit.SLE_Model_Graphical.SLE_Model_Declarative.abstract import (
    AbstractDeclarativeFactor,
)


class AbstractModelFactor(FactorKW, AbstractDeclarativeFactor, ABC):
    @property
    def prior_model(self):
        return self._prior_model

    def __init__(
        self,
        prior_model,
        factor,
        optimiser,
        prior_variable_dict,
        name=None,
        include_prior_factors=True,
    ):
        """
        A factor in the graph that actually computes the likelihood of a model
        given values for each variable that model contains

        Parameters
        ----------
        prior_model
            A model with some dimensionality
        optimiser
            A custom optimiser that will be used to fit this factor specifically
            instead of the default optimiser
        """
        self._prior_model = prior_model
        self.optimiser = optimiser
        super().__init__(
            factor, **prior_variable_dict, name=(name or namer(self.__class__.__name__))
        )
        self.include_prior_factors = include_prior_factors

    @property
    def info(self):
        """
        Info describing this factor. Same as model info with the factor name.

        Output as part of graph.info
        """
        return f"""{self.name}

{self.prior_model.info}"""

    def make_results_text(self, model_approx):
        """
        Create a string describing the posterior values after this factor
        during or after an EPOptimisation.

        Parameters
        ----------
        model_approx: EPMeanField

        Returns
        -------
        A string containing the name of this factor with the names and
        values of each associated variable in the mean field.
        """
        arguments = {
            prior: model_approx.mean_field[prior] for prior in self.prior_model.priors
        }
        updated_model = self.prior_model.gaussian_prior_model_for_arguments(arguments)
        formatter = TextFormatter()
        for (path, prior) in updated_model.path_priors_tuples:
            formatter.add(path, prior.mean)
        return f"""{self.name}

{formatter.text}"""
