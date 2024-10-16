import math
from abc import ABC, abstractmethod
from copy import copy
from functools import reduce
from inspect import getfullargspec
from itertools import count
from numbers import Real
from operator import and_
from typing import Dict, Tuple, Iterator
from typing import Optional, Union, Type, List
import numpy as np
from SLE_Model_Autoconf import cached_property
from SLE_Model_Autofit.SLE_Model_Mapper.variable import Variable
from SLE_Model_Autofit.SLE_Model_Messages.interface import MessageInterface

enforce_id_match = True


def update_array(arr1, ind, arr2):
    if np.shape(arr1):
        out = arr1.copy()
        out[ind] = arr2
        return out
    return arr2


class AbstractMessage(MessageInterface, ABC):
    _Base_class: Optional[Type["AbstractMessage"]] = None
    _projection_class: Optional[Type["AbstractMessage"]] = None
    _multivariate: bool = False
    _parameter_support: Optional[Tuple[(Tuple[(float, float)], ...)]] = None
    _support: Optional[Tuple[(Tuple[(float, float)], ...)]] = None
    ids = count()

    def __init__(
        self,
        *parameters: Union[(np.ndarray, float)],
        log_norm=0.0,
        lower_limit=(-math.inf),
        upper_limit=math.inf,
        id_=None,
    ):
        self.lower_limit = lower_limit
        self.upper_limit = upper_limit
        self.id = next(self.ids) if (id_ is None) else id_
        self.log_norm = log_norm
        self._broadcast = np.broadcast(*parameters)
        if self.shape:
            self.parameters = tuple((np.asanyarray(p) for p in parameters))
        else:
            self.parameters = tuple(parameters)

    @property
    def broadcast(self):
        return self._broadcast

    @property
    def _init_kwargs(self):
        return dict(
            log_norm=self.log_norm,
            id_=self.id,
            lower_limit=self.lower_limit,
            upper_limit=self.upper_limit,
        )

    def check_support(self):
        if self._parameter_support is not None:
            return reduce(
                and_,
                (
                    ((p >= support[0]) & (p <= support[1]))
                    for (p, support) in zip(self.parameters, self._parameter_support)
                ),
            )
        elif self.ndim:
            return np.array(True, dtype=bool, ndmin=self.ndim)
        return np.array([True])

    @property
    def multivariate(self):
        return self._multivariate

    def copy(self):
        cls = self._Base_class or type(self)
        result = cls(
            *(copy(params) for params in self.parameters),
            log_norm=self.log_norm,
            lower_limit=self.lower_limit,
            upper_limit=self.upper_limit,
        )
        result.id = self.id
        return result

    def __bool__(self):
        return True

    @abstractmethod
    def sample(self, n_samples=None):
        pass

    @staticmethod
    @abstractmethod
    def invert_natural_parameters(natural_parameters):
        pass

    @cached_property
    @abstractmethod
    def variance(self):
        pass

    @cached_property
    def scale(self):
        return self.std

    @cached_property
    def std(self):
        return self.variance**0.5

    def __hash__(self):
        return self.id

    def __iter__(self):
        return iter(self.parameters)

    @classmethod
    def _cached_attrs(cls):
        for n in dir(cls):
            attr = getattr(cls, n)
            if isinstance(attr, cached_property):
                (yield n)

    def _reset_cache(self):
        for attr in self._cached_attrs():
            self.__dict__.pop(attr, None)

    def __getitem__(self, index):
        cls = self._Base_class or type(self)
        if index == ():
            return self
        else:
            return cls(*(param[index] for param in self.parameters))

    def __setitem__(self, index, value):
        self._reset_cache()
        for (param0, param1) in zip(self.parameters, value.parameters):
            param0[index] = param1

    def merge(self, index, value):
        cls = self._Base_class or type(self)
        return cls(
            *(
                update_array(param0, index, param1)
                for (param0, param1) in zip(self.parameters, value.parameters)
            )
        )

    @classmethod
    def from_natural_parameters(cls, natural_parameters, **kwargs):
        cls_ = cls._projection_class or cls._Base_class or cls
        args = cls_.invert_natural_parameters(natural_parameters)
        return cls_(*args, **kwargs)

    def zeros_like(self):
        return self**0.0

    @classmethod
    @abstractmethod
    def invert_sufficient_statistics(cls, sufficient_statistics):
        pass

    @classmethod
    def from_sufficient_statistics(cls, suff_stats, **kwargs):
        natural_params = cls.invert_sufficient_statistics(suff_stats)
        cls_ = cls._projection_class or cls._Base_class or cls
        return cls_.from_natural_parameters(natural_params, **kwargs)

    def __mul__(self, other):
        if isinstance(other, MessageInterface):
            return self._multiply(other)
        else:
            cls = self._Base_class or type(self)
            log_norm = self.log_norm + np.log(other)
            return cls(
                *self.parameters,
                log_norm=log_norm,
                id_=self.id,
                lower_limit=self.lower_limit,
                upper_limit=self.upper_limit,
            )

    def __rmul__(self, other):
        return self * other

    def __truediv__(self, other):
        if isinstance(other, MessageInterface):
            return self._divide(other)
        else:
            cls = self._Base_class or type(self)
            log_norm = self.log_norm - np.log(other)
            return cls(
                *self.parameters,
                log_norm=log_norm,
                id_=self.id,
                lower_limit=self.lower_limit,
                upper_limit=self.upper_limit,
            )

    def __pow__(self, other):
        natural = self.natural_parameters
        new_params = other * natural
        log_norm = other * self.log_norm
        new = self.from_natural_parameters(
            new_params,
            log_norm=log_norm,
            id_=self.id,
            lower_limit=self.lower_limit,
            upper_limit=self.upper_limit,
        )
        return new

    @classmethod
    def parameter_names(cls):
        return getfullargspec(cls.__init__).args[1:(-1)]

    def __str__(self):
        param_attrs = [
            (attr, np.asanyarray(getattr(self, attr)))
            for attr in self.parameter_names()
        ]
        if self.shape:
            pad = max((len(attr) for (attr, _) in param_attrs))
            attr_str = "    {:<%d}={}" % pad
            param_strs = """,
""".join(
                (
                    attr_str.format(
                        attr, np.array2string(val, prefix=(" " * (pad + 5)))
                    )
                    for (attr, val) in param_attrs
                )
            )
            return f"""{type(self).__name__}(
{param_strs})"""
        else:
            param_strs = ", ".join(
                (
                    (
                        (attr + "=")
                        + np.array2string(val, prefix=(" " * (len(attr) + 1)))
                    )
                    for (attr, val) in param_attrs
                )
            )
            return f"{type(self).__name__}({param_strs})"

    __repr__ = __str__

    def factor(self, x):
        return self.logpdf(x)

    @classmethod
    def project(cls, samples, log_weight_list=None, **kwargs):
        """Calculates the sufficient statistics of a set of samples
        and returns the distribution with the appropriate parameters
        that match the sufficient statistics
        """
        if log_weight_list is None:
            log_weight_list = np.zeros_like(samples)
        log_w_max = np.max(log_weight_list, axis=0, keepdims=True)
        w = np.exp((log_weight_list - log_w_max))
        norm = w.mean(0)
        log_norm = np.log(norm) + log_w_max[0]
        tx = cls.to_canonical_form(samples)
        w /= norm
        suff_stats = (tx * w[(None, ...)]).mean(1)
        assert np.isfinite(suff_stats).all()
        cls_ = cls._projection_class or cls._Base_class or cls
        return cls_.from_sufficient_statistics(suff_stats, log_norm=log_norm, **kwargs)

    @classmethod
    def from_mode(cls, mode, covariance, **kwargs):
        pass

    def log_normalisation(self, *elems: Union[("AbstractMessage", float)]):
        """
        Calculates the log of the integral of the product of a
        set of distributions

        NOTE: ignores log normalisation
        """
        dists: List[MessageInterface] = [
            dist
            for dist in self._iter_dists(elems)
            if isinstance(dist, MessageInterface)
        ]
        log_norm = self.log_base_measure - self.log_partition
        log_norm += sum(
            ((dist.log_base_measure - dist.log_partition) for dist in dists)
        )
        prod_dist = self.sum_natural_parameters(*dists)
        log_norm -= prod_dist.log_base_measure - prod_dist.log_partition
        return log_norm

    def instance(self):
        return self

    def update_invalid(self, other):
        valid = self.check_valid()
        if self.ndim:
            valid_parameters: Iterator[np.ndarray] = (
                np.where(valid, p, p_safe) for (p, p_safe) in zip(self, other)
            )
        else:
            valid_parameters = iter((self if valid else other))
        cls = self._Base_class or type(self)
        new = cls(
            *valid_parameters,
            log_norm=self.log_norm,
            id_=self.id,
            lower_limit=self.lower_limit,
            upper_limit=self.upper_limit,
        )
        return new

    @staticmethod
    def _get_mean_variance(mean, covariance):
        (mean, covariance) = (np.asanyarray(mean), np.asanyarray(covariance))
        if not covariance.shape:
            variance = covariance * np.ones_like(mean)
            if not variance.shape:
                variance = variance.item()
        elif mean.shape == covariance.shape:
            variance = np.asanyarray(covariance)
        elif covariance.shape == (mean.shape * 2):
            inds = tuple(np.indices(mean.shape))
            variance = np.asanyarray(covariance)[(inds * 2)]
        else:
            raise ValueError(
                f"shape of covariance {covariance.shape} is invalid must be (), {mean.shape}, or {(mean.shape * 2)}"
            )
        return (mean, variance)

    def __call__(self, x):
        return np.sum(self.logpdf(x))

    def factor_jacobian(self, x, _variables=("x",)):
        (loglike, g) = self.logpdf_gradient(x)
        g = np.expand_dims(g, list(range(loglike.ndim)))
        return (loglike.sum(), (g,))

    def as_factor(self, variable, name=None):
        from SLE_Model_Autofit.SLE_Model_Graphical.SLE_Model_FactorGraphs import Factor

        if name is None:
            shape = self.shape
            clsname = type(self).__name__
            family = clsname[:(-7)] if clsname.endswith("Message") else clsname
            name = f"{family}Likelihood" + (str(shape) if shape else "")
        return Factor(
            self,
            variable,
            name=name,
            factor_jacobian=self.factor_jacobian,
            plates=variable.plates,
            arg_names=["x"],
        )

    def calc_exact_update(self, x):
        return (self,)

    def has_exact_projection(self, x):
        return type(self) is type(x)

    @classmethod
    def _reconstruct(cls, parameters, log_norm, id_, lower_limit, upper_limit, *args):
        return cls(
            *parameters,
            log_norm=log_norm,
            id_=id_,
            lower_limit=lower_limit,
            upper_limit=upper_limit,
        )

    def __reduce__(self):
        return (
            self._reconstruct,
            (
                self.parameters,
                self.log_norm,
                self.id,
                self.lower_limit,
                self.upper_limit,
            ),
        )

    def _sample(self, n_samples):
        return self.sample(n_samples)

    @classmethod
    def _logpdf_gradient(cls, self, x):
        return cls.logpdf_gradient(self, x)

    @classmethod
    def _logpdf_gradient_hessian(cls, self, x):
        return cls.logpdf_gradient_hessian(self, x)


def map_dists(dists, values, _call="logpdf"):
    """
    Calls a method (default: logpdf) for each Message in dists
    on the corresponding value in values
    """
    for v in dists.keys() & values.keys():
        dist = dists[v]
        if isinstance(dist, MessageInterface):
            (yield (v, getattr(dist, _call)(values[v])))
