import logging
from functools import wraps
from typing import Tuple, Callable, List, Union, Optional
import numpy as np
from VIS_CTI_Autofit.VIS_CTI_Graphical.VIS_CTI_FactorGraphs import Factor
from VIS_CTI_Autofit.VIS_CTI_Graphical.utils import Status
from VIS_CTI_Autofit.VIS_CTI_Graphical.VIS_CTI_ExpectationPropagation.ep_mean_field import (
    EPMeanField,
)
from VIS_CTI_Autofit import exc

logger = logging.getLogger(__name__)
EPCallBack = Callable[([Factor, EPMeanField, Status], bool)]


def default_inf(func):
    """
    Decorator that catches HistoryException and returns inf.

    This used to give infinite divergence when there is insufficient
    history for a given factor.
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except exc.HistoryException:
            return float("inf")

    return wrapper


class FactorHistory:
    def __init__(self, factor):
        """
        Tracks the history of a single factor

        Parameters
        ----------
        factor
            A factor in a graph undergoing optimisation
        """
        self.factor = factor
        self.history = list()

    def __call__(self, approx, status):
        """
        Add an optimisation result to the factor's history

        Parameters
        ----------
        approx
            The posterior mean field for an optimisation of the factor
        status
            Describes whether the optimisation was successful
        """
        self.history.append((approx, status))

    @property
    def successes(self):
        """
        A list of mean fields produced by successful optimisations
        """
        return [approx for (approx, success) in self.history if success]

    @property
    def latest_successful(self):
        """
        A mean field for the last successful optimisation
        """
        try:
            return self.successes[(-1)]
        except IndexError:
            raise exc.HistoryException(
                f"There have been no successful optimisations for factor {self.factor}"
            )

    @property
    def previous_successful(self):
        """
        A mean field for the last-but-one successful optimisation
        """
        try:
            return self.successes[(-2)]
        except IndexError:
            raise exc.HistoryException(
                f"There have been one or no successful optimisations for factor {self.factor}"
            )

    @default_inf
    def kl_divergence(self):
        """
        The KL Divergence between the mean fields produced by the last
        two successful optimisations.

        If there are less than two successful optimisations then this is
        infinite.
        """
        return self.latest_successful.mean_field.kl(self.previous_successful.mean_field)

    @default_inf
    def evidence_divergence(self):
        """
        The difference in the evidences between produced by the last two
        successful optimisations.

        If there are less than two successful optimisations then this is
        infinite.
        """
        return (
            self.latest_successful.log_evidence - self.previous_successful.log_evidence
        )

    @property
    def evidences(self):
        """
        Evidences from successful optimisations with None as a placeholder
        when optimisation failed.
        """
        return [
            (approx.log_evidence if status else None)
            for (approx, status) in self.history
        ]

    @property
    def kl_divergences(self):
        """
        Evidences from successful optimisations with None as a placeholder
        when optimisation failed.
        """
        divergences = []
        for i in range(1, len(self.history)):
            (previous, previous_success) = self.history[(i - 1)]
            (current, current_success) = self.history[i]
            if previous_success and current_success:
                divergences.append(current.mean_field.kl(previous.mean_field))
            else:
                divergences.append(None)
        return divergences


class EPHistory:
    def __init__(self, callbacks=(), kl_tol=0.1, evidence_tol=None):
        """
        Track the history an an EP Optimization.

        Facilitates computation of termination metrics.

        Parameters
        ----------
        callbacks
            Custom callbacks which can be used to terminate
            optimisation
        kl_tol
            The minimum KL Divergence between the mean fields
            produced by two consecutive optimisations below which
            optimisation is terminated.

            If None this termination condition is ignored.
        evidence_tol
            The minimum difference in evidence between the mean
            fields produced by two consecutive optimisations below
            which optimisation is terminated.

            If None this termination condition is ignored.
        """
        self._callbacks = callbacks
        self.history = {}
        self.kl_tol = kl_tol
        self.evidence_tol = evidence_tol

    def __getitem__(self, factor):
        """
        Retrieve the history associated with a given factor.
        """
        try:
            return self.history[factor]
        except KeyError:
            self.history[factor] = FactorHistory(factor)
            return self.history[factor]

    def items(self):
        return self.history.items()

    def __call__(self, factor, approx, status=Status()):
        """
        Add history for a given factor and determine whether optimisation
        should terminate.

        Parameters
        ----------
        factor
            A factor in the optimisation
        approx
            A mean field produced by optimisation of the factor
        status
            A status describing whether the optimisation was successful

        Returns
        -------
        A boolean indicating whether optimisation should terminate because
        divergence has dropped below a given tolerance or a callback evaluated
        to True.
        """
        self[factor](approx, status)
        if status.success:
            if any([callback(factor, approx, status) for callback in self._callbacks]):
                return True
            return self.is_converged(factor)
        return False

    def is_kl_converged(self, factor):
        """
        True if the KL Divergence between the mean fields produced by
        two consecutive, successful optimisations is below the specified
        tolerance.
        """
        return self[factor].kl_divergence() < self.kl_tol

    def is_kl_evidence_converged(self, factor):
        """
        True if the difference in evidence between produced by two consecutive,
        successful optimisations is below the specified tolerance.
        """
        evidence_divergence = self[factor].evidence_divergence()
        if evidence_divergence < 0:
            logger.warning(f"Evidence for factor {factor} has decreased")
        return abs(evidence_divergence) < self.evidence_tol

    def is_converged(self, factor):
        """
        True if either convergence condition is met.
        """
        if self.kl_tol and self.is_kl_converged(factor):
            return True
        if self.evidence_tol and self.is_kl_evidence_converged(factor):
            return True
        return False
