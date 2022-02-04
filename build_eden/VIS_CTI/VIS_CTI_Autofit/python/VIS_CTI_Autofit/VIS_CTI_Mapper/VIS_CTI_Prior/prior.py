import numpy as np
from VIS_CTI_Autoconf import conf
from VIS_CTI_Autofit import exc
from VIS_CTI_Autofit.VIS_CTI_Messages.normal import NormalMessage, UniformNormalMessage
from VIS_CTI_Autofit.VIS_CTI_Messages.transform import log_10_transform
from VIS_CTI_Autofit.VIS_CTI_Messages.transform_wrapper import (
    TransformedWrapperInstance,
)
from VIS_CTI_Autofit.VIS_CTI_Mapper.VIS_CTI_Prior.abstract import (
    epsilon,
    assert_within_limits,
)


class Limits:
    @staticmethod
    def for_class_and_attributes_name(cls, attribute_name):
        limit_dict = conf.instance.prior_config.for_class_and_suffix_path(
            cls, [attribute_name, "gaussian_limits"]
        )
        return (limit_dict["lower"], limit_dict["upper"])


class WrappedInstance(TransformedWrapperInstance):
    __identifier_fields__ = ("lower_limit", "upper_limit")
    __database_args__ = ("lower_limit", "upper_limit", "log_norm", "id_")

    def __init__(self, transformed_wrapper, *args, lower_limit, upper_limit, **kwargs):
        super().__init__(
            transformed_wrapper,
            *args,
            lower_limit=lower_limit,
            upper_limit=upper_limit,
            **kwargs,
        )
        self.lower_limit = lower_limit
        self.upper_limit = upper_limit
        if self.lower_limit >= self.upper_limit:
            raise exc.PriorException(
                "The upper limit of a prior must be greater than its lower limit"
            )

    def _new_for_base_message(self, message):
        return type(self)(
            lower_limit=self.lower_limit,
            upper_limit=self.upper_limit,
            id_=self.instance().id,
            params=message.parameters,
        )


class UniformPrior(WrappedInstance):
    "A prior with a uniform distribution between a lower and upper limit"

    def __init__(self, lower_limit=0.0, upper_limit=1.0, id_=None, params=(0.0, 1.0)):
        if any(map(np.isnan, params)):
            raise exc.MessageException("nan parameter passed to UniformPrior")
        lower_limit = float(lower_limit)
        upper_limit = float(upper_limit)
        Message = UniformNormalMessage.shifted(
            shift=lower_limit, scale=(upper_limit - lower_limit)
        )
        super().__init__(
            Message, *params, lower_limit=lower_limit, upper_limit=upper_limit, id_=id_
        )

    def logpdf(self, x):
        if x == self.lower_limit:
            x += epsilon
        elif x == self.upper_limit:
            x -= epsilon
        return self.instance().logpdf(x)

    def __str__(self):
        "The line of text describing this prior for the model_mapper.info file"
        return f"UniformPrior, lower_limit = {self.lower_limit}, upper_limit = {self.upper_limit}"

    @assert_within_limits
    def value_for(self, unit):
        """

        Parameters
        ----------
        unit: Float
            A unit hypercube value between 0 and 1
        Returns
        -------
        value: Float
            A value for the attribute between the upper and lower limits
        """
        return round(super().value_for(unit), 14)

    @staticmethod
    def log_prior_from_value(value):
        """
        Returns the log prior of a physical value, so the log likelihood of a model evaluation can be converted to a
        posterior as log_prior + log_likelihood.

        This is used by Emcee in the log likelihood function evaluation.

        NOTE: For a UniformPrior this is always zero, provided the value is between the lower and upper limit. Given
        this is check for when the instance is made (in the *instance_from_vector* function), we thus can simply return
        zero in this function.
        """
        return 0.0


class LogUniformPrior(WrappedInstance):
    "A prior with a uniform distribution between a lower and upper limit"

    def __init__(cls, lower_limit=1e-06, upper_limit=1.0, id_=None, params=(0.0, 1.0)):
        if lower_limit <= 0.0:
            raise exc.PriorException(
                "The lower limit of a LogUniformPrior cannot be zero or negative."
            )
        lower_limit = float(lower_limit)
        upper_limit = float(upper_limit)
        Message = UniformNormalMessage.shifted(
            shift=np.log10(lower_limit), scale=np.log10((upper_limit / lower_limit))
        ).transformed(log_10_transform)
        super().__init__(
            Message, *params, id_=id_, lower_limit=lower_limit, upper_limit=upper_limit
        )

    __identifier_fields__ = ("lower_limit", "upper_limit")

    @staticmethod
    def log_prior_from_value(value):
        """
        Returns the log prior of a physical value, so the log likelihood of a model evaluation can be converted to a
            posterior as log_prior + log_likelihood.

        This is used by Emcee in the log likelihood function evaluation.

        Parameters
        ----------
        value : float
            The physical value of this prior's corresponding parameter in a `NonLinearSearch` sample."""
        return 1.0 / value

    @assert_within_limits
    def value_for(self, unit):
        return super().value_for(unit)

    def __str__(self):
        "The line of text describing this prior for the model_mapper.info file"
        return f"LogUniformPrior, lower_limit = {self.lower_limit}, upper_limit = {self.upper_limit}"


class GaussianPrior(NormalMessage):
    "A prior with a gaussian distribution"
    __identifier_fields__ = ("lower_limit", "upper_limit", "mean", "sigma")

    @assert_within_limits
    def value_for(self, unit):
        """

        Parameters
        ----------
        unit: Float
            A unit hypercube value between 0 and 1

        Returns
        -------
        value: Float
            A value for the attribute biased to the gaussian distribution
        """
        return super().value_for(unit)
