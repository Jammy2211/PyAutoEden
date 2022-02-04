from typing import Type, Tuple, Union
import numpy as np
from VIS_CTI_Autoconf import cached_property
from VIS_CTI_Autofit.VIS_CTI_Messages.abstract import AbstractMessage
from VIS_CTI_Autofit.VIS_CTI_Messages.transform import AbstractDensityTransform


class TransformedMessage(AbstractMessage):
    _Message: Type[AbstractMessage]
    _transform: Union[(AbstractDensityTransform, Type[AbstractDensityTransform])]
    _depth = 0

    def __init__(self, *args, **kwargs):
        self.instance = self._Message(*args, **kwargs)
        super().__init__(
            *self.instance.parameters,
            log_norm=self.instance.log_norm,
            lower_limit=self.instance.lower_limit,
            upper_limit=self.instance.upper_limit,
            id_=self.instance.id
        )

    @property
    def natural_parameters(self):
        return self.instance.natural_parameters

    @property
    def log_partition(self):
        return self.instance.log_partition

    def __getattr__(self, item):
        if item == "__setstate__":
            raise AttributeError()
        return getattr(self.instance, item)

    @classmethod
    def invert_natural_parameters(cls, natural_parameters):
        return cls._Message.invert_natural_parameters(natural_parameters)

    @classmethod
    def invert_sufficient_statistics(cls, sufficient_statistics):
        return cls._Message.invert_sufficient_statistics(sufficient_statistics)

    def value_for(self, unit):
        return self._transform.inv_transform(self.instance.value_for(unit))

    @classmethod
    def _reconstruct(
        cls,
        Message,
        clsname,
        transform,
        parameters,
        log_norm,
        id_,
        lower_limit,
        upper_limit,
    ):
        Transformed = Message.transformed(transform, clsname)
        return Transformed(
            *parameters,
            log_norm=log_norm,
            id_=id_,
            lower_limit=lower_limit,
            upper_limit=upper_limit
        )

    def __reduce__(self):
        return (
            TransformedMessage._reconstruct,
            (
                self._Message,
                self.__class__.__name__,
                self._transform,
                self.parameters,
                self.log_norm,
                self.id,
                self.lower_limit,
                self.upper_limit,
            ),
        )

    @classmethod
    def calc_log_base_measure(cls, x):
        x = cls._transform.transform(x)
        log_base = cls._Message.calc_log_base_measure(x)
        return log_base

    @classmethod
    def to_canonical_form(cls, x):
        x = cls._transform.transform(x)
        return cls._Message.to_canonical_form(x)

    @cached_property
    def mean(self):
        return self._transform.inv_transform(self.instance.mean)

    @cached_property
    def variance(self):
        jac = self._transform.jacobian(self.instance.mean)
        return jac.quad(self._Message.variance.func(self))

    def _sample(self, n_samples):
        x = self.instance._sample(n_samples)
        return self._transform.inv_transform(x)

    @classmethod
    def _factor(cls, self, x):
        (x, log_det) = cls._transform.transform_det(x)
        eta = self._broadcast_natural_parameters(x)
        t = cls._Message.to_canonical_form(x)
        log_base = self.calc_log_base_measure(x) + log_det
        return self.natural_logpdf(eta, t, log_base, self.log_partition)

    @classmethod
    def _factor_gradient(cls, self, x):
        (x, logd, logd_grad, jac) = cls._transform.transform_det_jac(x)
        (logl, grad) = cls._Message._logpdf_gradient(self, x)
        return ((logl + logd), ((grad * jac) + logd_grad))

    def factor(self, x):
        return self._factor(self, x)

    def factor_gradient(self, x):
        return self._factor_gradient(self, x)

    @classmethod
    def _logpdf_gradient(cls, self, x):
        (x, jac) = cls._transform.transform_jac(x)
        (logl, grad) = cls._Message._logpdf_gradient(self, x)
        return (logl, (grad * jac))

    def sample(self, n_samples=None):
        return self._sample(n_samples)

    def logpdf_gradient(self, x):
        return self._logpdf_gradient(self, x)
