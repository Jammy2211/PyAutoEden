import logging
from abc import ABC, abstractmethod
from typing import Tuple
from SLE_Model_Autofit.SLE_Model_Graphical.mean_field import (
    MeanField,
    FactorApproximation,
    Status,
)
from SLE_Model_Autofit.SLE_Model_Graphical.utils import LogWarnings

logger = logging.getLogger(__name__)


class AbstractFactorOptimiser(ABC):
    """
    An optimiser used to optimise individual factors during EPOptimisation.
    """

    logger = logger.debug

    def __init__(self, initial_values=None, inplace=False):
        self.initial_values = initial_values or {}
        self.inplace = inplace

    @abstractmethod
    def optimise(self, factor_approx, status=Status()):
        pass

    def exact_fit(self, factor_approx, status=Status()):
        factor = factor_approx.factor
        cavity_dist = factor_approx.cavity_dist
        with LogWarnings(logger=self.logger, action="always") as caught_warnings:
            if factor._calc_exact_update:
                factor_mean_field = factor.calc_exact_update(cavity_dist)
                new_model_dist = factor_mean_field * cavity_dist
            elif factor._calc_exact_projection:
                new_model_dist = factor.calc_exact_projection(cavity_dist)
            else:
                raise NotImplementedError("Factor does not have exact updates methods")
        return (new_model_dist, status)


class ExactFactorFit(AbstractFactorOptimiser):
    optimise = AbstractFactorOptimiser.exact_fit