from abc import ABC, abstractmethod
from typing import Set, List, Dict, Optional
from VIS_CTI_Autofit.VIS_CTI_Graphical.VIS_CTI_Declarative.VIS_CTI_Factor.prior import (
    PriorFactor,
)
from VIS_CTI_Autofit.VIS_CTI_Graphical.VIS_CTI_Declarative.graph import (
    DeclarativeFactorGraph,
)
from VIS_CTI_Autofit.VIS_CTI_Graphical.VIS_CTI_Declarative.result import EPResult
from VIS_CTI_Autofit.VIS_CTI_Graphical.VIS_CTI_ExpectationPropagation import (
    AbstractFactorOptimiser,
)
from VIS_CTI_Autofit.VIS_CTI_Graphical.VIS_CTI_ExpectationPropagation import EPMeanField
from VIS_CTI_Autofit.VIS_CTI_Graphical.VIS_CTI_ExpectationPropagation import EPOptimiser
from VIS_CTI_Autofit.VIS_CTI_Mapper.model import ModelInstance
from VIS_CTI_Autofit.VIS_CTI_Mapper.VIS_CTI_Prior.abstract import Prior
from VIS_CTI_Autofit.VIS_CTI_Mapper.VIS_CTI_PriorModel.collection import (
    CollectionPriorModel,
)
from VIS_CTI_Autofit.VIS_CTI_Messages.normal import NormalMessage
from VIS_CTI_Autofit.VIS_CTI_NonLinear.VIS_CTI_Analysis import Analysis
from VIS_CTI_Autofit.VIS_CTI_NonLinear.VIS_CTI_Paths.abstract import AbstractPaths


class AbstractDeclarativeFactor(Analysis, ABC):
    optimiser: AbstractFactorOptimiser

    @property
    @abstractmethod
    def name(self):
        pass

    @property
    def model_factors(self):
        return [self]

    @property
    @abstractmethod
    def prior_model(self):
        pass

    @property
    @abstractmethod
    def info(self):
        pass

    @property
    def priors(self):
        """
        A set of all priors encompassed by the contained likelihood models
        """
        return {
            prior for model in self.model_factors for prior in model.prior_model.priors
        }

    @property
    def prior_factors(self):
        """
        A list of factors that act as priors on latent variables. One factor exists
        for each unique prior.
        """
        return list(map(PriorFactor, sorted(self.priors)))

    @property
    def message_dict(self):
        """
        Dictionary mapping priors to messages.
        """
        return {prior: prior for prior in self.priors}

    @property
    def graph(self):
        """
        The complete graph made by combining all factors and priors
        """
        return DeclarativeFactorGraph(
            ([model for model in self.model_factors] + self.prior_factors)
        )

    def mean_field_approximation(self):
        """
        Returns a EPMeanField of the factor graph
        """
        return EPMeanField.from_approx_dists(self.graph, self.message_dict)

    def _make_ep_optimiser(self, optimiser, paths=None):
        return EPOptimiser(
            self.graph,
            default_optimiser=optimiser,
            factor_optimisers={
                factor: factor.optimiser
                for factor in self.model_factors
                if (factor.optimiser is not None)
            },
            paths=paths,
        )

    def optimise(self, optimiser, paths=None, **kwargs):
        """
        Use an EP Optimiser to optimise the graph associated with this collection
        of factors and create a Collection to represent the results.

        Parameters
        ----------
        paths
            Optionally define how data should be output. This paths
            object is copied to every optimiser.
        optimiser
            An optimiser that acts on graphs

        Returns
        -------
        A collection of prior models
        """
        opt = self._make_ep_optimiser(optimiser, paths=paths)
        updated_ep_mean_field = opt.run(self.mean_field_approximation(), **kwargs)
        return EPResult(
            ep_history=opt.ep_history,
            declarative_factor=self,
            updated_ep_mean_field=updated_ep_mean_field,
        )

    def visualize(self, paths, instance, during_analysis):
        """
        Visualise the instances provided using each factor.

        Instances in the ModelInstance must have the same order as the factors.

        Parameters
        ----------
        paths
            Object describing where data should be saved to
        instance
            A collection of instances, each corresponding to a factor
        during_analysis
            Is this visualisation during analysis?
        """
        for (model_factor, instance) in zip(self.model_factors, instance):
            model_factor.visualize(paths, instance, during_analysis)

    @property
    def global_prior_model(self):
        """
        A collection of prior models, with one model for each factor.
        """
        return GlobalPriorModel(self)


class GlobalPriorModel(CollectionPriorModel):
    def __init__(self, factor):
        """
        A global model comprising all factors which can be used to compare
        results between global optimisation and expectation propagation.

        Parameters
        ----------
        factor
            A factor comprising one or more factors, usually a graph
        """
        super().__init__(
            [model_factor.prior_model for model_factor in factor.model_factors]
        )
        self.factor = factor

    @property
    def info(self):
        """
        A string describing the collection of factors in the graphical style
        """
        return self.factor.graph.info
