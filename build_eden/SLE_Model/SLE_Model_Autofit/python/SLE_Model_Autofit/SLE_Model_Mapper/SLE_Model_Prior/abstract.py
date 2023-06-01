import itertools
import os
import random
from abc import ABC, abstractmethod
from copy import copy
from typing import Union, Tuple
from SLE_Model_Autoconf import conf
from SLE_Model_Autofit import exc
from SLE_Model_Autofit.SLE_Model_Mapper.SLE_Model_Prior.SLE_Model_Arithmetic import (
    ArithmeticMixin,
)
from SLE_Model_Autofit.SLE_Model_Mapper.SLE_Model_Prior.deferred import DeferredArgument
from SLE_Model_Autofit.SLE_Model_Mapper.variable import Variable

epsilon = 1e-14


class Prior(Variable, ABC, ArithmeticMixin):
    __database_args__ = ("lower_limit", "upper_limit", "id_")
    _ids = itertools.count()

    def __init__(self, message, lower_limit=0.0, upper_limit=1.0, id_=None):
        """
        An object used to mappers a unit value to an attribute value for a specific
        class attribute.

        Parameters
        ----------
        lower_limit: Float
            The lowest value this prior can return
        upper_limit: Float
            The highest value this prior can return
        """
        if id_ is None:
            id_ = next(self._ids)
        super().__init__(id_=id_)
        self.message = message
        message.id_ = id_
        self.lower_limit = float(lower_limit)
        self.upper_limit = float(upper_limit)
        if self.lower_limit >= self.upper_limit:
            raise exc.PriorException(
                "The upper limit of a prior must be greater than its lower limit"
            )
        self.width_modifier = None

    @property
    def lower_unit_limit(self):
        """
        The lower limit for this prior in unit vector space
        """
        return self.unit_value_for(self.lower_limit)

    @property
    def upper_unit_limit(self):
        """
        The upper limit for this prior in unit vector space
        """
        return self.unit_value_for(self.upper_limit)

    def unit_value_for(self, physical_value):
        """
        Compute the unit value between 0 and 1 for the physical value.
        """
        return self.message.cdf(physical_value)

    def with_message(self, message):
        new = copy(self)
        new.message = message
        return new

    def new(self):
        """
        Returns a copy of this prior with a new id assigned making it distinct
        """
        new = copy(self)
        new.id = next(self._ids)
        return new

    def with_limits(self, lower_limit, upper_limit):
        """
        Create a new instance of the same prior class with the passed limits.
        """
        new = self.__class__(
            lower_limit=max(lower_limit, self.lower_limit),
            upper_limit=min(upper_limit, self.upper_limit),
        )
        new.message = self.message
        return new

    @property
    def factor(self):
        """
        A callable PDF used as a factor in factor graphs
        """
        return self.message.factor

    def assert_within_limits(self, value):
        if conf.instance["general"]["model"]["ignore_prior_limits"] or (
            os.environ.get("PYAUTOFIT_TEST_MODE") == "1"
        ):
            return
        if not (self.lower_limit <= value <= self.upper_limit):
            raise exc.PriorLimitException(
                "The physical value {} for a prior was not within its limits {}, {}".format(
                    value, self.lower_limit, self.upper_limit
                )
            )

    @staticmethod
    def for_class_and_attribute_name(cls, attribute_name):
        prior_dict = conf.instance.prior_config.for_class_and_suffix_path(
            cls, [attribute_name]
        )
        return Prior.from_dict(prior_dict)

    @property
    def width(self):
        return self.upper_limit - self.lower_limit

    def random(self, lower_limit=0.0, upper_limit=1.0):
        """
        A random value sampled from this prior
        """
        return self.value_for(
            random.uniform(
                max(lower_limit, self.lower_unit_limit),
                min(upper_limit, self.upper_unit_limit),
            )
        )

    def value_for(self, unit, ignore_prior_limits=False):
        """
        Return a physical value for a value between 0 and 1 with the transformation
        described by this prior.

        Parameters
        ----------
        unit
            A unit value between 0 and 1.

        Returns
        -------
        A physical value, mapped from the unit value accoridng to the prior.
        """
        result = self.message.value_for(unit)
        if not ignore_prior_limits:
            self.assert_within_limits(result)
        return result

    def instance_for_arguments(self, arguments):
        return arguments[self]

    def project(self, samples, weights):
        result = copy(self)
        result.message = self.message.project(
            samples=samples,
            log_weight_list=weights,
            id_=self.id,
            lower_limit=self.lower_limit,
            upper_limit=self.upper_limit,
        )
        return result

    def __getattr__(self, item):
        if item in ("__setstate__", "__getstate__"):
            raise AttributeError(item)
        return getattr(self.message, item)

    def __eq__(self, other):
        try:
            return self.id == other.id
        except AttributeError:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash(self.id)

    def __repr__(self):
        return "<{} id={} lower_limit={} upper_limit={}>".format(
            self.__class__.__name__, self.id, self.lower_limit, self.upper_limit
        )

    def __str__(self):
        "The line of text describing this prior for the model_mapper.info file"
        return f"{self.__class__.__name__} [{self.id}], {self.parameter_string}"

    @property
    @abstractmethod
    def parameter_string(self):
        pass

    def __float__(self):
        return self.value_for(0.5)

    @classmethod
    def from_dict(cls, prior_dict):
        """
        Returns a prior from a JSON representation.

        Parameters
        ----------
        prior_dict : dict
            A dictionary representation of a prior including a type (e.g. Uniform) and all constructor arguments.

        Returns
        -------
        An instance of a child of this class.
        """
        if prior_dict["type"] == "Constant":
            return prior_dict["value"]
        if prior_dict["type"] == "Deferred":
            return DeferredArgument()
        from SLE_Model_Autofit.SLE_Model_Mapper.SLE_Model_Prior.uniform import (
            UniformPrior,
        )
        from SLE_Model_Autofit.SLE_Model_Mapper.SLE_Model_Prior.log_uniform import (
            LogUniformPrior,
        )
        from SLE_Model_Autofit.SLE_Model_Mapper.SLE_Model_Prior.gaussian import (
            GaussianPrior,
        )
        from SLE_Model_Autofit.SLE_Model_Mapper.SLE_Model_Prior.log_gaussian import (
            LogGaussianPrior,
        )

        prior_type_dict = {
            "Uniform": UniformPrior,
            "LogUniform": LogUniformPrior,
            "Gaussian": GaussianPrior,
            "LogGaussian": LogGaussianPrior,
        }
        return prior_type_dict[prior_dict["type"]](
            **{
                key: value
                for (key, value) in prior_dict.items()
                if (key not in ("type", "width_modifier", "gaussian_limits"))
            }
        )

    def dict(self):
        """
        A dictionary representation of this prior
        """
        prior_dict = {
            "lower_limit": self.lower_limit,
            "upper_limit": self.upper_limit,
            "type": self.name_of_class(),
        }
        return prior_dict

    @classmethod
    def name_of_class(cls):
        """
        A string name for the class, with the prior suffix removed.
        """
        return cls.__name__.replace("Prior", "")

    @property
    def limits(self):
        return (self.lower_limit, self.upper_limit)

    def gaussian_prior_model_for_arguments(self, arguments):
        return arguments[self]