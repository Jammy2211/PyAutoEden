from typing import Optional
import numpy as np
from SLE_Model_Autofit.SLE_Model_Graphical.SLE_Model_ExpectationPropagation import (
    AbstractFactorOptimiser,
)
from SLE_Model_Autofit.SLE_Model_Mapper.model import ModelInstance
from SLE_Model_Autofit.SLE_Model_Mapper.SLE_Model_PriorModel.prior_model import (
    AbstractPriorModel,
)
from SLE_Model_Autofit.SLE_Model_NonLinear.SLE_Model_Analysis import Analysis
from SLE_Model_Autofit.SLE_Model_NonLinear.SLE_Model_Paths.abstract import AbstractPaths
from SLE_Model_Autofit.SLE_Model_Graphical.SLE_Model_Declarative.SLE_Model_Factor.abstract import (
    AbstractModelFactor,
)


class AnalysisFactor(AbstractModelFactor):
    @property
    def prior_model(self):
        return self._prior_model

    def __init__(self, prior_model, analysis, optimiser=None, name=None):
        """
        A factor in the graph that actually computes the likelihood of a model
        given values for each variable that model contains

        Parameters
        ----------
        prior_model
            A model with some dimensionality
        analysis
            A class that implements a function which evaluates how well an
            instance of the model fits some data
        optimiser
            A custom optimiser that will be used to fit this factor specifically
            instead of the default optimiser
        """
        self.label = prior_model.label
        self.analysis = analysis

        def _factor(**kwargs: np.ndarray):
            """
            Returns an instance of the prior model and evaluates it, forming
            a factor.

            Parameters
            ----------
            kwargs
                Arguments with names that are unique for each prior.

            Returns
            -------
            Calculated likelihood
            """
            arguments = dict()
            for (name_, array) in kwargs.items():
                prior_id = int(name_.split("_")[1])
                prior = prior_model.prior_with_id(prior_id)
                arguments[prior] = array
            instance = prior_model.instance_for_arguments(arguments)
            return analysis.log_likelihood_function(instance)

        prior_variable_dict = {prior.name: prior for prior in prior_model.priors}
        super().__init__(
            prior_model=prior_model,
            factor=_factor,
            optimiser=optimiser,
            prior_variable_dict=prior_variable_dict,
            name=name,
        )

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state):
        self.__dict__.update(state)

    def __getattr__(self, item):
        return getattr(self.prior_model, item)

    def name_for_variable(self, variable):
        path = ".".join(self.prior_model.path_for_prior(variable))
        return f"{self.name}.{path}"

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
        self.analysis.visualize(
            paths=paths, instance=instance, during_analysis=during_analysis
        )
        self.analysis.visualize_combined(
            analyses=None,
            paths=paths,
            instance=instance,
            during_analysis=during_analysis,
        )

    def log_likelihood_function(self, instance):
        return self.analysis.log_likelihood_function(instance)