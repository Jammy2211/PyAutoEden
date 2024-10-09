from typing import Union, List
from SLE_Model_Autofit.SLE_Model_Graphical.SLE_Model_Declarative.SLE_Model_Factor.hierarchical import (
    HierarchicalFactor,
)
from SLE_Model_Autofit.SLE_Model_Graphical.SLE_Model_ExpectationPropagation import (
    EPHistory,
)
from SLE_Model_Autofit.SLE_Model_Graphical.SLE_Model_ExpectationPropagation.ep_mean_field import (
    EPMeanField,
)
from SLE_Model_Autofit.SLE_Model_Graphical.SLE_Model_FactorGraphs.factor import Factor
from SLE_Model_Autofit.SLE_Model_Mapper.SLE_Model_PriorModel.abstract import (
    AbstractPriorModel,
)
from SLE_Model_Autofit.SLE_Model_Mapper.SLE_Model_PriorModel.collection import (
    Collection,
)
from SLE_Model_Autofit.SLE_Model_NonLinear.result import Result, AbstractResult
from SLE_Model_Autofit.SLE_Model_NonLinear.SLE_Model_Samples.samples import Samples


class HierarchicalResult(AbstractResult):
    def __init__(self, results):
        """
        One true factor is created per each variable drawn from the declarative
        hierarchical factor. One result for each of those factors is in this
        collection.

        Parameters
        ----------
        results
            Results from hierarchical factor optimisations
        """
        super().__init__(results[0].sigma)
        self.results = results

    @property
    def samples(self):
        """
        All samples from all underlying optimisations are summed together.
        """
        return sum((result.samples for result in self.results))

    @property
    def model(self):
        """
        Priors with the same path in the model are combined by taking the
        product of their underlying messages. i.e. the product of the
        posteriors.

        The distribution model is returned.
        """
        return AbstractPriorModel.product(
            (result.model for result in self.results)
        ).distribution_model

    @property
    def instance(self):
        """
        Return the instance (e.g. prior) describing the distribution
        from which samples are drawn.
        """
        return super().instance.distribution_model


class EPResult:
    def __init__(self, ep_history, declarative_factor, updated_ep_mean_field):
        """
        The result of an EP Optimisation including its history, a declarative
        representation of the optimised graph and the resultant EPMeanField
        which comprises factors and resultant approximations of variables.

        Parameters
        ----------
        ep_history
            A history of the optimisation
        declarative_factor: AbstractDeclarativeFactor
            A declarative representation of the factor being optimised
        updated_ep_mean_field
            An updated mean field; effectively the result of the optimisation
        """
        self.ep_history = ep_history
        self.declarative_factor = declarative_factor
        self.updated_ep_mean_field = updated_ep_mean_field

    @property
    def model(self):
        """
        A collection populated with messages representing the posteriors of
        the EP Optimisation. Each item in the collection represents a single
        factor in the optimisation.
        """
        collection = Collection(
            {
                factor.name: factor.prior_model
                for factor in self.declarative_factor.model_factors
            }
        )
        arguments = {
            prior: prior.with_message(self.updated_ep_mean_field.mean_field[prior])
            for prior in collection.priors
        }
        return collection.gaussian_prior_model_for_arguments(arguments)

    @property
    def latest_results(self):
        """
        A list of results for all analysis and hierarchical factors.
        """
        return [
            self.ep_history[factor].latest_result
            for factor in self.declarative_factor.model_factors
        ]

    @property
    def instance(self):
        """
        The median instance taken from the updated model
        """
        return self.model.instance_from_prior_medians()

    def latest_for(self, factor):
        """
        Return the latest result for a factor.

        If the factor is hierarchical return the latest result for
        the first true factor (i.e. for one of the drawn variable)

        Parameters
        ----------
        factor
            A factor from the graph

        Returns
        -------
        The latest result for that factor
        """
        if isinstance(factor, HierarchicalFactor):
            results = [
                self.ep_history[child_factor].latest_result
                for child_factor in factor.factors
            ]
            return HierarchicalResult(results)
        return self.ep_history[factor].latest_result
