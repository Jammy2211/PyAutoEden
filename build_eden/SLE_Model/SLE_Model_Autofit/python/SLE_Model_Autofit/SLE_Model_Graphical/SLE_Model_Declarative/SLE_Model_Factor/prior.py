from SLE_Model_Autofit.SLE_Model_Graphical.SLE_Model_FactorGraphs.factor import FactorKW
from SLE_Model_Autofit.SLE_Model_Mapper.SLE_Model_Prior.abstract import Prior
from SLE_Model_Autofit.SLE_Model_Mapper.SLE_Model_PriorModel.collection import (
    Collection,
)
from SLE_Model_Autofit.SLE_Model_NonLinear.SLE_Model_Analysis import Analysis
from SLE_Model_Autofit.SLE_Model_Tools.namer import namer


class PriorFactor(FactorKW, Analysis):
    def __init__(self, prior):
        """
        A factor that wraps a prior such that is can be optimised
        by classic AutoFit optimisers.

        To do this it implements a prior_model and analysis.

        Parameters
        ----------
        prior
            A message/prior, usually of another factor. Prior factors
            are generated programmatically.
        """
        super().__init__(prior.factor, x=prior, name=namer(self.__class__.__name__))
        self.prior = prior
        self.label = f"PriorFactor({prior.label})"

    @property
    def _unique_representation(self):
        return (self.prior, self.arg_names, self.args, self.deterministic_variables)

    @property
    def prior_model(self):
        """
        A trivial prior model to conform to the expected interface.
        """
        return Collection(self.prior)

    @property
    def analysis(self):
        """
        This is the analysis class for a PriorFactor
        """
        return self

    def log_likelihood_function(self, instance):
        """
        Compute the likelihood.

        The instance is a collection with a single argument expressing a
        possible value for this prior. The likelihood is computed by simply
        evaluating the prior's PDF for the given value.
        """
        return self.prior.factor(instance[0])

    @property
    def variable(self):
        return list(self.variables)[0]
