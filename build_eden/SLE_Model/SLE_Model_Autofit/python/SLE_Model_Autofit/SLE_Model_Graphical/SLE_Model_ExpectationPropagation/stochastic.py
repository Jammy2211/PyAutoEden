import logging
from typing import Dict, List, Generator
from SLE_Model_Autofit.SLE_Model_Graphical.SLE_Model_ExpectationPropagation.ep_mean_field import (
    EPMeanField,
)
from SLE_Model_Autofit.SLE_Model_Graphical.mean_field import Status
from SLE_Model_Autofit.SLE_Model_Graphical.utils import StatusFlag, LogWarnings
from SLE_Model_Autofit.SLE_Model_Mapper.variable import Plate
from SLE_Model_Autofit.SLE_Model_Tools.util import IntervalCounter
from SLE_Model_Autofit.SLE_Model_Graphical.SLE_Model_ExpectationPropagation.optimiser import (
    EPOptimiser,
)

logger = logging.getLogger(__name__)


class StochasticEPOptimiser(EPOptimiser):
    def factor_step(self, factor, subset_approx, optimiser):
        factor_logger = logging.getLogger(factor.name)
        factor_logger.debug("Optimising...")
        subset_factor = subset_approx._factor_subset_factor[factor]
        try:
            with LogWarnings(
                logger=factor_logger.debug, action="always"
            ) as caught_warnings:
                factor_approx = subset_approx.factor_approximation(factor)
                (new_model_dist, status) = optimiser.optimise(factor_approx)
                (subset_approx, status) = self.updater.update_model_approx(
                    new_model_dist, factor_approx, subset_approx, status
                )
            messages = status.messages + tuple(caught_warnings.messages)
            status = Status(status.success, messages, status.flag)
        except (ValueError, ArithmeticError, RuntimeError) as e:
            logger.exception(e)
            status = Status(
                False,
                (status.messages + (f"Factor: {factor} experienced error {e}",)),
                StatusFlag.FAILURE,
            )
        factor_logger.debug(status)
        return (subset_approx, status)

    def run(
        self,
        model_approx,
        batches,
        log_interval=10,
        visualise_interval=100,
        output_interval=10,
        inplace=False,
    ):
        """
        Run the optimisation on an approximation of the model.

        Parameters
        ----------
        model_approx
            A collection of messages describing priors on the model's variables.
        max_steps
            The maximum number of steps prior to termination. Termination may also
            occur when difference in log evidence or KL Divergence drop below a given
            threshold for two consecutive optimisations of a given factor.
        log_interval
            How steps should we wait before logging information?
        visualise_interval
            How steps should we wait before visualising information?
            This includes plots of KL Divergence and Evidence.
        output_interval
            How steps should we wait before outputting information?
            This includes the model.results file which describes the current mean values
            of each message.

        Returns
        -------
        An updated approximation of the model
        """
        should_log = IntervalCounter(log_interval)
        should_visualise = IntervalCounter(visualise_interval)
        should_output = IntervalCounter(output_interval)
        for batch in batches:
            subset_approx = model_approx[batch]
            for (factor, optimiser) in self.factor_optimisers.items():
                (subset_approx, status) = self.factor_step(
                    factor, subset_approx, optimiser
                )
                if status and should_log():
                    self._log_factor(factor)
                if self.ep_history(factor, subset_approx, status):
                    logger.info("Terminating optimisation")
                    break
            else:
                if inplace:
                    model_approx[batch] = subset_approx
                else:
                    model_approx = model_approx.merge(batch, subset_approx)
                if self.ep_history(model_approx.factor_graph, model_approx):
                    logger.info("Terminating optimisation")
                    break
                if should_visualise():
                    self.visualiser()
                if should_output():
                    self._output_results(model_approx)
                continue
            break
        self.visualiser()
        self._output_results(model_approx)
        return model_approx
