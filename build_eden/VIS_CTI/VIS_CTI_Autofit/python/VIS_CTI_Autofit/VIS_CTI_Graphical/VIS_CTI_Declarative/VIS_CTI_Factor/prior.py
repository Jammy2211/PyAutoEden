from VIS_CTI_Autofit.VIS_CTI_Graphical.VIS_CTI_FactorGraphs.factor import Factor
from VIS_CTI_Autofit.VIS_CTI_Mapper.VIS_CTI_Prior.abstract import Prior
from VIS_CTI_Autofit.VIS_CTI_Mapper.VIS_CTI_PriorModel.collection import (
    CollectionPriorModel,
)
from VIS_CTI_Autofit.VIS_CTI_NonLinear.VIS_CTI_Analysis import Analysis
from VIS_CTI_Autofit.VIS_CTI_Tools.namer import namer


class PriorFactor(Factor, Analysis):
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

    @property
    def prior_model(self):
        """
        A trivial prior model to conform to the expected interface.
        """
        return CollectionPriorModel(self.prior)

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
