import configparser
import logging
import os
import random
from abc import ABC, abstractmethod
from typing import Dict, Tuple, List, Optional
import numpy as np
from SLE_Model_Autofit import exc
from SLE_Model_Autofit.SLE_Model_NonLinear.SLE_Model_Paths.abstract import AbstractPaths
from SLE_Model_Autofit.SLE_Model_Mapper.SLE_Model_Prior.abstract import Prior
from SLE_Model_Autofit.SLE_Model_Mapper.SLE_Model_PriorModel.abstract import (
    AbstractPriorModel,
)
from SLE_Model_Autofit.SLE_Model_NonLinear.SLE_Model_Parallel import SneakyPool

logger = logging.getLogger(__name__)


class AbstractInitializer(ABC):
    """
    Family of classes used to provide initial points for non-linear search
    """

    @abstractmethod
    def _generate_unit_parameter_list(self, model):
        pass

    def info_from_model(self, model):
        raise NotImplementedError

    @staticmethod
    def figure_of_metric(args):
        (fitness, parameter_list) = args
        try:
            figure_of_merit = fitness(parameters=parameter_list)
            if np.isnan(figure_of_merit) or (figure_of_merit < (-1e98)):
                return None
            return figure_of_merit
        except exc.FitException:
            return None

    def samples_from_model(
        self,
        total_points,
        model,
        fitness,
        paths,
        use_prior_medians=False,
        test_mode_samples=True,
        n_cores=1,
    ):
        """
        Generate the initial points of the non-linear search, by randomly drawing unit values from a uniform
        distribution between the ball_lower_limit and ball_upper_limit values.

        Parameters
        ----------
        total_points
            The number of points in non-linear paramemter space which initial points are created for.
        model
            An object that represents possible instances of some model with a given dimensionality which is the number
            of free dimensions of the model.
        """
        if (os.environ.get("PYAUTOFIT_TEST_MODE") == "1") and test_mode_samples:
            return self.samples_in_test_mode(total_points=total_points, model=model)
        unit_parameter_lists = []
        parameter_lists = []
        figures_of_merit_list = []
        sneaky_pool = SneakyPool(n_cores, fitness, paths)
        logger.info(f"Generating initial samples of model using {n_cores} cores")
        while len(figures_of_merit_list) < total_points:
            remaining_points = total_points - len(figures_of_merit_list)
            batch_size = min(remaining_points, n_cores)
            parameter_lists_ = []
            unit_parameter_lists_ = []
            for _ in range(batch_size):
                if not use_prior_medians:
                    unit_parameter_list = self._generate_unit_parameter_list(model)
                else:
                    unit_parameter_list = [0.5] * model.prior_count
                parameter_list = model.vector_from_unit_vector(
                    unit_vector=unit_parameter_list
                )
                parameter_lists_.append(parameter_list)
                unit_parameter_lists_.append(unit_parameter_list)
            for (figure_of_merit, unit_parameter_list, parameter_list) in zip(
                sneaky_pool.map(
                    function=self.figure_of_metric,
                    args_list=[
                        (fitness, parameter_list) for parameter_list in parameter_lists_
                    ],
                    log_info=False,
                ),
                unit_parameter_lists_,
                parameter_lists_,
            ):
                if figure_of_merit is not None:
                    unit_parameter_lists.append(unit_parameter_list)
                    parameter_lists.append(parameter_list)
                    figures_of_merit_list.append(figure_of_merit)
        if (total_points > 1) and np.allclose(
            a=figures_of_merit_list[0], b=figures_of_merit_list[1:]
        ):
            raise exc.InitializerException(
                """
                The initial samples all have the same figure of merit (e.g. log likelihood values).
                
                The non-linear search will therefore not progress correctly.
                
                Possible causes for this behaviour are:
                
                - The `log_likelihood_function` of the analysis class is defined incorrectly.
                - The model parameterization creates numerically inaccurate log likelihoods.
                - The`log_likelihood_function`  is always returning `nan` values.            
                """
            )
        logger.info(f"Initial samples generated, starting non-linear search")
        return (unit_parameter_lists, parameter_lists, figures_of_merit_list)

    def samples_in_test_mode(self, total_points, model):
        """
        Generate the initial points of the non-linear search in test mode. Like normal, test model draws points, by
        randomly drawing unit values from a uniform distribution between the ball_lower_limit and ball_upper_limit
        values.

        However, the log likelihood function is bypassed and all likelihoods are returned with a value -1.0e99. This
        is so that integration testing of large-scale model-fitting projects can be performed efficiently by bypassing
        sampling of points using the `log_likelihood_function`.

        Parameters
        ----------
        total_points
            The number of points in non-linear paramemter space which initial points are created for.
        model
            An object that represents possible instances of some model with a given dimensionality which is the number
            of free dimensions of the model.
        """
        logger.warning(
            f"TEST MODE ON: SAMPLES BEING ASSIGNED ABRITRARY LARGE LIKELIHOODS"
        )
        unit_parameter_lists = []
        parameter_lists = []
        figure_of_merit_list = []
        point_index = 0
        figure_of_merit = -1e99
        while point_index < total_points:
            try:
                unit_parameter_list = self._generate_unit_parameter_list(model)
                parameter_list = model.vector_from_unit_vector(
                    unit_vector=unit_parameter_list
                )
                model.instance_from_vector(vector=parameter_list)
                unit_parameter_lists.append(unit_parameter_list)
                parameter_lists.append(parameter_list)
                figure_of_merit_list.append(figure_of_merit)
                figure_of_merit *= 10.0
                point_index += 1
            except exc.FitException:
                pass
        return (unit_parameter_lists, parameter_lists, figure_of_merit_list)


class InitializerParamBounds(AbstractInitializer):
    def __init__(self, parameter_dict, lower_limit=0.0, upper_limit=1.0):
        """
        Initializer which uses the bounds on input parameters as the starting point for the search (e.g. where
        an MLE optimization starts or MCMC walkers are initialized).

        Parameters
        ----------
        parameter_dict
            A dictionary mapping each parameter path to bounded ranges of physical values that
            are where the search begins.
        lower_limit
            A default, unit lower limit used when a prior is not specified
        upper_limit
            A default, unit upper limit used when a prior is not specified
        """
        self.parameter_dict = parameter_dict
        self.lower_limit = lower_limit
        self.upper_limit = upper_limit
        self._generated_warnings = set()

    def _generate_unit_parameter_list(self, model):
        """
        Generate a unit vector for the model. The default limits are used for any
        priors which the model has but are not found in the parameter dict.

        Parameters
        ----------
        model
            A model for which initial points are required

        Returns
        -------
        A unit vector
        """
        unit_parameter_list = []
        for prior in model.priors_ordered_by_id:
            try:
                (lower, upper) = map(prior.unit_value_for, self.parameter_dict[prior])
                value = random.uniform(lower, upper)
            except KeyError:
                key = ".".join(model.path_for_prior(prior))
                if key not in self._generated_warnings:
                    logger.warning(
                        f"Range for {key} not set in the InitializerParamBounds. Using defaults."
                    )
                    self._generated_warnings.add(key)
                lower = self.lower_limit
                upper = self.upper_limit
                value = prior.unit_value_for(prior.random(lower, upper))
            unit_parameter_list.append(value)
        return unit_parameter_list

    def info_from_model(self, model):
        """
        Returns a string showing the bounds of the parameters in the initializer.
        """
        info = (
            ("Total Free Parameters = " + str(model.prior_count))
            + """
"""
        )
        info += (
            ("Total Starting Points = " + str(len(self.parameter_dict)))
            + """

"""
        )
        for prior in model.priors_ordered_by_id:
            key = ".".join(model.path_for_prior(prior))
            try:
                value = self.info_value_from(self.parameter_dict[prior])
                info += f"""{key}: Start[{value}]
"""
            except KeyError:
                info += f"""{key}: {prior})
"""
        return info

    def info_value_from(self, value):
        """
        Returns the value that is used to display the bounds of the parameters in the initializer.

        This function simply returns the input value, but it can be overridden in subclasses for diffferent
        initializers.

        Parameters
        ----------
        value
            The value to be displayed in the initializer info which is a tuple of the lower and upper bounds of the
            parameter.
        """
        return value


class InitializerParamStartPoints(InitializerParamBounds):
    def __init__(self, parameter_dict):
        """
        Initializer which input values of the parameters as the starting point for the search (e.g. where
        an MLE optimization starts or MCMC walkers are initialized).

        Parameters
        ----------
        parameter_dict
            A dictionary mapping each parameter path to the starting point physical values that
            are where the search begins.
        lower_limit
            A default, unit lower limit used when a prior is not specified
        upper_limit
            A default, unit upper limit used when a prior is not specified
        """
        parameter_dict_new = {}
        for (key, value) in parameter_dict.items():
            parameter_dict_new[key] = ((value - 1e-08), (value + 1e-08))
        super().__init__(parameter_dict=parameter_dict_new)

    def info_value_from(self, value):
        """
        Returns the value that is used to display the starting point of the parameters in the initializer.

        This function returns the mean of the input value, as the starting point is a single value in the center of the
        bounds.

        Parameters
        ----------
        value
            The value to be displayed in the initializer info which is a tuple of the lower and upper bounds of the
            parameter.
        """
        return (value[1] + value[0]) / 2.0


class Initializer(AbstractInitializer):
    def __init__(self, lower_limit, upper_limit):
        """
        The Initializer creates the initial set of samples in non-linear parameter space that can be passed into a
        `NonLinearSearch` to define where to begin sampling.

        Although most non-linear searches have in-built functionality to do this, some do not cope well with parameter
        resamples that are raised as FitException's. Thus, PyAutoFit uses its own initializer to bypass these problems.
        """
        self.lower_limit = lower_limit
        self.upper_limit = upper_limit

    @classmethod
    def from_config(cls, config):
        """
        Load the Initializer from a non_linear config file.
        """
        try:
            initializer = config("initialize", "method")
        except configparser.NoSectionError:
            return None
        if initializer in "prior":
            return InitializerPrior()
        elif initializer in "ball":
            ball_lower_limit = config("initialize", "ball_lower_limit")
            ball_upper_limit = config("initialize", "ball_upper_limit")
            return InitializerBall(
                lower_limit=ball_lower_limit, upper_limit=ball_upper_limit
            )

    def _generate_unit_parameter_list(self, model):
        return model.random_unit_vector_within_limits(
            lower_limit=self.lower_limit, upper_limit=self.upper_limit
        )


class InitializerPrior(Initializer):
    def __init__(self):
        """
        The Initializer creates the initial set of samples in non-linear parameter space that can be passed into a
        `NonLinearSearch` to define where to begin sampling.

        Although most non-linear searches have in-built functionality to do this, some do not cope well with parameter
        resamples that are raised as FitException's. Thus, PyAutoFit uses its own initializer to bypass these problems.

        The InitializerPrior class generates from the priors, by drawing all values as unit values between 0.0 and 1.0
        and mapping them to physical values via the prior.
        """
        super().__init__(lower_limit=0.0, upper_limit=1.0)


class InitializerBall(Initializer):
    def __init__(self, lower_limit, upper_limit):
        """
        The Initializer creates the initial set of samples in non-linear parameter space that can be passed into a
        `NonLinearSearch` to define where to begin sampling.

        Although most non-linear searches have in-built functionality to do this, some do not cope well with parameter
        resamples that are raised as FitException's. Thus, PyAutoFit uses its own initializer to bypass these problems.

        The InitializerBall class generates the samples in a small compact volume or 'ball' in parameter space, which is
        the recommended initialization strategy for the MCMC `NonLinearSearch` Emcee.

        Parameters
        ----------
        lower_limit
            The lower limit of the uniform distribution unit values are drawn from when initializing walkers in a small
            compact ball.
        upper_limit
            The upper limit of the uniform distribution unit values are drawn from when initializing walkers in a small
            compact ball.
        """
        super().__init__(lower_limit=lower_limit, upper_limit=upper_limit)
