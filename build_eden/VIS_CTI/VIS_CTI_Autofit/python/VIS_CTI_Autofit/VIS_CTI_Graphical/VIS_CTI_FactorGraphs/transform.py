from abc import abstractmethod
from typing import Dict, Tuple, Optional, List
import numpy as np
from scipy.linalg import cho_factor
from VIS_CTI_Autofit.VIS_CTI_Mapper.operator import (
    CholeskyOperator,
    InvCholeskyTransform,
    IdentityOperator,
    DiagonalMatrix,
)
from VIS_CTI_Autoconf import cached_property
from VIS_CTI_Autofit.VIS_CTI_Graphical.VIS_CTI_FactorGraphs.abstract import (
    AbstractNode,
    Value,
    FactorValue,
    JacobianValue,
    HessianValue,
)
from VIS_CTI_Autofit.VIS_CTI_Graphical.utils import Axis
from VIS_CTI_Autofit.VIS_CTI_Mapper.variable import Variable


class VariableTransform:
    """
    """

    def __init__(self, transforms):
        self.transforms = transforms

    def __mul__(self, values):
        return {k: (M * values[k]) for (k, M) in self.transforms.items()}

    def __rtruediv__(self, values):
        return {k: (values[k] / M) for (k, M) in self.transforms.items()}

    def __rmul__(self, values):
        return {k: (values[k] * M) for (k, M) in self.transforms.items()}

    def ldiv(self, values):
        return {k: M.ldiv(values[k]) for (k, M) in self.transforms.items()}

    rdiv = __rtruediv__
    rmul = __rmul__
    lmul = __mul__
    __matmul__ = __mul__

    def quad(self, values):
        return {
            v: (H.T if np.ndim(H) else H) for (v, H) in (values * self).items()
        } * self

    def invquad(self, values):
        return {
            v: (H.T if np.ndim(H) else H) for (v, H) in (values / self).items()
        } / self

    @cached_property
    def log_det(self):
        return sum((M.log_det for M in self.transforms.values()))

    @classmethod
    def from_scales(cls, scales):
        return cls({v: DiagonalMatrix(scale) for (v, scale) in scales.items()})

    @classmethod
    def from_covariances(cls, covs):
        return cls(
            {v: InvCholeskyTransform(cho_factor(cov)) for (v, cov) in covs.items()}
        )

    @classmethod
    def from_inv_covariances(cls, inv_covs):
        return cls(
            {
                v: CholeskyOperator(cho_factor(inv_cov))
                for (v, inv_cov) in inv_covs.items()
            }
        )


class FullCholeskyTransform(VariableTransform):
    def __init__(self, cholesky, param_shapes):
        self.cholesky = cholesky
        self.param_shapes = param_shapes

    @classmethod
    def from_optresult(cls, opt_result):
        param_shapes = opt_result.param_shapes
        cov = opt_result.result.hess_inv
        if not isinstance(cov, np.ndarray):
            cov = cov.todense()
        return cls(InvCholeskyTransform.from_dense(cov), param_shapes)

    def __mul__(self, values):
        (M, x) = (self.cholesky, self.param_shapes.flatten(values))
        return self.param_shapes.unflatten((M * x))

    def __rtruediv__(self, values):
        (M, x) = (self.cholesky, self.param_shapes.flatten(values))
        return self.param_shapes.unflatten((x / M))

    def __rmul__(self, values):
        (M, x) = (self.cholesky, self.param_shapes.flatten(values))
        return self.param_shapes.unflatten((x * M))

    @abstractmethod
    def ldiv(self, values):
        (M, x) = (self.cholesky, self.param_shapes.flatten(values))
        return self.param_shapes.unflatten(M.ldiv(x))

    rdiv = __rtruediv__
    rmul = __rmul__
    lmul = __mul__
    __matmul__ = __mul__

    @cached_property
    def log_det(self):
        return self.cholesky.log_det


class IdentityVariableTransform(VariableTransform):
    def __init__(self):
        pass

    def _identity(self, values):
        return values

    __mul__ = _identity
    __rtruediv__ = _identity
    __rmul__ = _identity
    ldiv = _identity
    rdiv = __rtruediv__
    rmul = __rmul__
    lmul = __mul__
    __matmul__ = __mul__
    quad = _identity
    invquad = _identity

    @property
    def log_det(self):
        return 0.0


identity_transform = IdentityOperator()
identity_variable_transform = IdentityVariableTransform()


class TransformedNode(AbstractNode):
    def __init__(self, node, transform):
        self.node = node
        self.transform = transform

    @property
    def variables(self):
        return self.node.variables

    @property
    def deterministic_variables(self):
        return self.node.deterministic_variables

    @property
    def all_variables(self):
        return self.node.all_variables

    @property
    def name(self):
        return f"FactorApproximation({self.node.name})"

    def __call__(self, values, axis=False):
        return self.node(self.transform.ldiv(values), axis=axis)

    def func_jacobian(
        self, values, variables=None, axis=None, _calc_deterministic=True, **kwargs
    ):
        (fval, jval) = self.node.func_jacobian(
            self.transform.ldiv(values),
            variables=variables,
            axis=axis,
            _calc_deterministic=_calc_deterministic,
        )
        grad = jval / self.transform
        return (fval, grad)

    def func_jacobian_hessian(
        self, values, variables=None, axis=None, _calc_deterministic=True, **kwargs
    ):
        M = self.transform
        (fval, jval, hval) = self.node.func_jacobian_hessian(
            M.ldiv(values),
            variables=variables,
            axis=axis,
            _calc_deterministic=_calc_deterministic,
        )
        grad = jval / M
        hess = M.invquad(hval)
        return (fval, grad, hess)

    def __getattribute__(self, name):
        try:
            return super().__getattribute__(name)
        except AttributeError:
            return getattr(self.node, name)
