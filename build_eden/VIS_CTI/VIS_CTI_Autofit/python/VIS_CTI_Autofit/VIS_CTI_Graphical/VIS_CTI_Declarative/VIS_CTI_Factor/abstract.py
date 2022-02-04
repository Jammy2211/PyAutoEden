from abc import ABC
from typing import Optional
from VIS_CTI_Autofit.VIS_CTI_Graphical.VIS_CTI_ExpectationPropagation import (
    AbstractFactorOptimiser,
)
from VIS_CTI_Autofit.VIS_CTI_Graphical.VIS_CTI_FactorGraphs.factor import Factor
from VIS_CTI_Autofit.VIS_CTI_Mapper.VIS_CTI_PriorModel.prior_model import (
    PriorModel,
    AbstractPriorModel,
)
from VIS_CTI_Autofit.VIS_CTI_Text.formatter import TextFormatter
from VIS_CTI_Autofit.VIS_CTI_Tools.namer import namer
from VIS_CTI_Autofit.VIS_CTI_Graphical.VIS_CTI_Declarative.abstract import (
    AbstractDeclarativeFactor,
)


class AbstractModelFactor(Factor, AbstractDeclarativeFactor, ABC):
    @property
    def prior_model(self):
        return self._prior_model

    def __init__(self, prior_model, factor, optimiser, prior_variable_dict, name=None):
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

    def optimise(self, optimiser, **kwargs):
        """
        Optimise this factor on its own returning a PriorModel
        representing the final state of the messages.

        Parameters
        ----------
        optimiser

        Returns
        -------
        A PriorModel representing the optimised factor
        """
        return super().optimise(optimiser, **kwargs).model[0]
