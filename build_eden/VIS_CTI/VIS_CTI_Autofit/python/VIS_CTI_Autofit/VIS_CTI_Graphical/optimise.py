from collections import defaultdict
from itertools import repeat
from typing import Optional, Dict, Tuple, Any, List, Iterator
import numpy as np
from scipy.optimize import minimize, OptimizeResult, least_squares, approx_fprime
from VIS_CTI_Autofit.VIS_CTI_Graphical.VIS_CTI_ExpectationPropagation import (
    EPMeanField,
    AbstractFactorOptimiser,
)
from VIS_CTI_Autofit.VIS_CTI_Graphical.VIS_CTI_FactorGraphs import (
    Variable,
    Factor,
    JacobianValue,
)
from VIS_CTI_Autofit.VIS_CTI_Graphical.VIS_CTI_FactorGraphs import transform as t
from VIS_CTI_Autofit.VIS_CTI_Graphical.mean_field import (
    MeanField,
    FactorApproximation,
    Status,
)
from VIS_CTI_Autofit.VIS_CTI_Graphical.utils import (
    propagate_uncertainty,
    FlattenArrays,
    OptResult,
)
from VIS_CTI_Autofit.VIS_CTI_Mapper.operator import LinearOperator
from VIS_CTI_Autofit.VIS_CTI_Messages.fixed import FixedMessage

ArraysDict = Dict[(Variable, np.ndarray)]


class OptFactor:
    """
    """

    def __init__(
        self,
        factor,
        param_shapes,
        fixed_kws=None,
        model_dist=None,
        transform=None,
        bounds=None,
        method="L-BFGS-B",
        jac=False,
        tol=None,
        options=None,
        callback=None,
        constraints=None,
    ):
        self.factor = factor
        self.param_shapes = param_shapes
        self._model_dist = model_dist
        self.jac = jac
        self.transform = t.identity_transform if (transform is None) else transform
        self.param_bounds = bounds
        self.free_vars = tuple(self.param_shapes.keys())
        self.deterministic_variables = self.factor.deterministic_variables
        self.sign = 1
        self.fixed_kws = fixed_kws or {}
        meth = method.lower()
        if meth not in ("bfgs", "l-bfgs-b"):
            raise ValueError(("Unknown solver %s" % method))
        self.method = meth
        if bounds:
            bounds = [
                b
                for (k, s) in self.param_shapes.items()
                for bound in bounds[k]
                for b in repeat(bound, np.prod(s, dtype=int))
            ]
            self.bounds = self.transform.transform_bounds(bounds)
        else:
            self.bounds = bounds
        self.default_kws = {
            "jac": self.jac,
            "bounds": self.bounds,
            "method": self.method,
            "constraints": constraints,
            "tol": tol,
            "callback": callback,
            "options": options,
        }

    @property
    def model_dist(self):
        if self._model_dist is None:
            raise ValueError("Model dist not defined")
        else:
            return self._model_dist

    @classmethod
    def from_approx(cls, factor_approx, transform=None):
        value_shapes = {}
        fixed_kws = {}
        bounds = {}
        for v in factor_approx.variables:
            dist = factor_approx.model_dist[v]
            if isinstance(dist, FixedMessage):
                fixed_kws[v] = dist.mean
            else:
                value_shapes[v] = dist.shape
                bounds[v] = dist._support
        return cls(
            factor_approx,
            FlattenArrays(value_shapes),
            fixed_kws=fixed_kws,
            model_dist=factor_approx.model_dist,
            transform=transform,
            bounds=bounds,
        )

    def flatten(self, values):
        x0 = self.param_shapes.flatten(values)
        return x0

    def unflatten(self, x0):
        values = {**self.param_shapes.unflatten(x0), **self.fixed_kws}
        return values

    def __call__(self, x0):
        values = self.unflatten(self.transform.ldiv(x0))
        return self.sign * np.sum(self.factor(values, axis=None))

    def func_jacobian(self, x0):
        values = self.unflatten(self.transform.ldiv(x0))
        (fval, jval) = self.factor.func_jacobian(
            values, self.free_vars, axis=None, _calc_deterministic=True
        )
        grad = self.flatten(jval) / self.transform
        return ((self.sign * fval.log_value), (self.sign * grad))

    def jacobian(self, args):
        return self.func_jacobian(args)[1]

    def numerically_verify_jacobian(self, n_tries=10, eps=1e-06, rtol=0.001, atol=0.01):
        x0s = (self.flatten(self.get_random_start()) for _ in range(n_tries))
        return all(
            (
                np.allclose(
                    self.jacobian(x0),
                    approx_fprime(x0, self, eps),
                    atol=atol,
                    rtol=rtol,
                )
                for x0 in x0s
            )
        )

    def get_random_start(self, arrays_dict=None):
        arrays_dict = arrays_dict or {}
        return {
            v: (arrays_dict[v] if (v in arrays_dict) else self.model_dist[v].sample())
            for v in self.free_vars
        }

    def _parse_result(self, result, status=Status()):
        (success, messages) = status
        success = result.success
        try:
            message = result.message.decode()
        except AttributeError:
            message = result.message
        messages += (
            f"optimise.find_factor_mode: nfev={result.nfev}, nit={result.nit}, status={result.status}, message={message}",
        )
        full_hess_inv = result.hess_inv
        if not isinstance(full_hess_inv, np.ndarray):
            full_hess_inv = full_hess_inv.todense()
        M = self.transform
        x = M.ldiv(result.x)
        full_hess_inv = M.ldiv(M.ldiv(full_hess_inv).T)
        mode = {**self.param_shapes.unflatten(x), **self.fixed_kws}
        hess_inv = self.param_shapes.unflatten(full_hess_inv)
        return OptResult(
            mode,
            hess_inv,
            (self.sign * result.fun),
            full_hess_inv,
            result,
            Status(success, messages),
        )

    def _minimise(self, arrays_dict, **kwargs):
        x0 = self.transform * self.param_shapes.flatten(arrays_dict)
        opt_kws = {**self.default_kws, **kwargs}
        func = self.func_jacobian if opt_kws["jac"] else self
        return minimize(func, x0, **opt_kws)

    def minimise(self, arrays_dict=None, status=Status(), **kwargs):
        self.sign = 1
        p0 = self.get_random_start((arrays_dict or {}))
        res = self._minimise(p0, **kwargs)
        return self._parse_result(res, status=status)

    def maximise(self, arrays_dict=None, status=Status(), **kwargs):
        self.sign = -1
        p0 = self.get_random_start((arrays_dict or {}))
        res = self._minimise(p0, **kwargs)
        return self._parse_result(res, status=status)

    minimize = minimise
    maximize = maximise


def update_det_cov(res, jacobian):
    """Calculates the inv hessian of the deterministic variables

    Note that this modifies res.
    """
    covars = res.hess_inv
    for (v, grad) in jacobian.items():
        for (det, jac) in grad.items():
            cov = propagate_uncertainty(covars[v], jac)
            covars[det] = covars.get(det, 0.0) + cov
    return res


class LaplaceFactorOptimiser(AbstractFactorOptimiser):
    def __init__(
        self,
        whiten_optimiser=True,
        transforms=None,
        deltas=None,
        initial_values=None,
        opt_kws=None,
        default_opt_kws=None,
        transform_cls=t.InvCholeskyTransform,
    ):
        self.whiten_optimiser = whiten_optimiser
        self.initial_values = {}
        if initial_values:
            self.initial_values.update(initial_values)
        self.transforms = defaultdict((lambda: t.identity_transform))
        if transforms:
            self.transforms.update(transforms)
        self.deltas = defaultdict((lambda: 1))
        if deltas:
            self.deltas.update(deltas)
        self.default_opt_kws = default_opt_kws or {}
        self.opt_kws = defaultdict(self.default_opt_kws.copy)
        if opt_kws:
            self.opt_kws.update(opt_kws)
        self.transform_cls = transform_cls

    def optimise(self, factor, model_approx, status=Status()):
        whiten = self.transforms[factor]
        delta = self.deltas[factor]
        opt_kws = self.opt_kws[factor]
        start = self.initial_values.get(factor)
        factor_approx = model_approx.factor_approximation(factor)
        opt = OptFactor.from_approx(factor_approx, transform=whiten)
        res = opt.maximise(start, status=status, **opt_kws)
        value = factor_approx.factor(res.mode)
        res.mode.update(value.deterministic_values)
        jacobian = factor_approx.factor.jacobian(res.mode, opt.free_vars, axis=None)
        update_det_cov(res, jacobian)
        self.transforms[factor] = self.transform_cls.from_dense(res.full_hess_inv)
        new_model_dist = factor_approx.model_dist.project_mode(res)
        (projection, status) = factor_approx.project(
            new_model_dist, delta=delta, status=res.status
        )
        (new_approx, status) = model_approx.project(projection, status)
        return (new_approx, status)


LaplaceFactorOptimizer = LaplaceFactorOptimiser


def maximise_factor_approx(factor_approx, **kwargs):
    """
    """
    p0 = {
        v: kwargs.pop(v, factor_approx.model_dist[v].sample(1)[0])
        for v in factor_approx.factor.variables
    }
    opt = OptFactor.from_approx(factor_approx, **kwargs)
    return opt.maximise(**p0)


maximize_factor_approx = maximise_factor_approx


def find_factor_mode(
    factor_approx, return_cov=True, status=Status(), min_iter=2, opt_kws=None, **kwargs
):
    """
    """
    opt_kws = {} if (opt_kws is None) else opt_kws
    opt = OptFactor.from_approx(factor_approx, **kwargs)
    res = opt.maximise(status=status, **opt_kws)
    if return_cov:
        value = factor_approx.factor(res.mode)
        res.mode.update(value.deterministic_values)
        jacobian = factor_approx.factor.jacobian(res.mode, opt.free_vars)
        update_det_cov(res, jacobian)
    return res


def laplace_factor_approx(
    model_approx, factor, delta=1.0, status=Status(), opt_kws=None
):
    opt_kws = {} if (opt_kws is None) else opt_kws
    factor_approx = model_approx.factor_approximation(factor)
    res = find_factor_mode(factor_approx, return_cov=True, status=status, **opt_kws)
    model_dist = factor_approx.model_dist.project_mode(res)
    (projection, status) = factor_approx.project(
        model_dist, delta=delta, status=res.status
    )
    (new_approx, status) = model_approx.project(projection, status=status)
    return (new_approx, status)


class LaplaceOptimiser:
    def __init__(self, n_iter=4, delta=1.0, opt_kws=None):
        self.history = dict()
        self.n_iter = n_iter
        self.delta = delta
        self.opt_kws = {} if (opt_kws is None) else opt_kws

    def step(self, model_approx, factors=None, status=Status()):
        new_approx = model_approx
        factors = model_approx.factor_graph.factors if (factors is None) else factors
        for factor in factors:
            (new_approx, status) = laplace_factor_approx(
                new_approx, factor, self.delta, status=status, opt_kws=self.opt_kws
            )
            (yield (factor, new_approx, status))

    def run(self, model_approx, factors=None, status=Status()):
        new_approx = model_approx
        for i in range(self.n_iter):
            for (factor, new_approx, status) in self.step(new_approx, factors):
                self.history[(i, factor)] = new_approx
        return (new_approx, status)


class LeastSquaresOpt:
    _opt_params = dict(
        jac="2-point",
        method="trf",
        ftol=1e-08,
        xtol=1e-08,
        gtol=1e-08,
        x_scale=1.0,
        loss="linear",
        f_scale=1.0,
        diff_step=None,
        tr_solver=None,
        tr_options={},
        jac_sparsity=None,
        max_nfev=None,
        verbose=0,
    )

    def __init__(
        self, factor_approx, fixed_kws=None, param_bounds=None, opt_only=None, **kwargs
    ):
        self.factor_approx = factor_approx
        self.opt_params = {**self._opt_params, **kwargs}
        param_shapes = {}
        param_bounds = {} if (param_bounds is None) else param_bounds
        fixed_kws = {} if (fixed_kws is None) else fixed_kws
        for v in factor_approx.factor.variables:
            dist = factor_approx.model_dist[v]
            if isinstance(dist, FixedMessage):
                fixed_kws[v] = dist.mean
            else:
                param_shapes[v] = dist.shape
                param_bounds[v] = dist._support
        self.fixed_kws = fixed_kws
        self.param_shapes = FlattenArrays(param_shapes)
        if opt_only is None:
            opt_only = tuple(
                (
                    v
                    for (v, d) in factor_approx.cavity_dist.items()
                    if (not isinstance(d, FixedMessage))
                )
            )
        self.opt_only = opt_only
        self.resid_means = {k: factor_approx.cavity_dist[k].mean for k in self.opt_only}
        self.resid_scales = {
            k: factor_approx.cavity_dist[k].scale for k in self.opt_only
        }
        self.resid_shapes = FlattenArrays(
            {k: np.shape(m) for (k, m) in self.resid_means.items()}
        )
        self.bounds = tuple(
            np.array(
                list(
                    zip(
                        *[
                            b
                            for (k, s) in param_shapes.items()
                            for bound in param_bounds[k]
                            for b in repeat(bound, np.prod(s, dtype=int))
                        ]
                    )
                )
            )
        )

    def __call__(self, arr):
        p0 = self.param_shapes.unflatten(arr)
        values = {**p0, **self.fixed_kws}
        fvals = self.factor_approx.factor(values)
        values.update(fvals.deterministic_values)
        residuals = {
            v: ((values[v] - mean) / self.resid_scales[v])
            for (v, mean) in self.resid_means.items()
        }
        return self.resid_shapes.flatten(residuals)

    def least_squares(self, values=None):
        values = values or {}
        model_dist = self.factor_approx.model_dist
        p0 = {
            v: (values[v] if (v in values) else model_dist[v].sample())
            for v in self.param_shapes.keys()
        }
        arr = self.param_shapes.flatten(p0)
        res = least_squares(self, arr, bounds=self.bounds, **self.opt_params)
        sol = self.param_shapes.unflatten(res.x)
        fval = self.factor_approx.factor({**sol, **self.fixed_kws})
        det_vars = fval.deterministic_values
        jac = {
            (d, k): b
            for (k, a) in self.param_shapes.unflatten(res.jac.T, ndim=1).items()
            for (d, b) in self.resid_shapes.unflatten(a.T, ndim=1).items()
        }
        hess = self.param_shapes.unflatten(res.jac.T.dot(res.jac))

        def inv(a):
            shape = np.shape(a)
            ndim = len(shape)
            if ndim:
                a = np.asanyarray(a)
                s = shape[: (ndim // 2)]
                n = np.prod(s, dtype=int)
                return np.linalg.inv(a.reshape(n, n)).reshape((s + s))
            else:
                return 1 / a

        invhess = {k: inv(h) for (k, h) in hess.items()}
        for det in det_vars:
            invhess[det] = 0.0
            for v in sol:
                invhess[det] += propagate_uncertainty(invhess[v], jac[(det, v)])
        mode = {**sol, **det_vars}
        return (mode, invhess, res)


def lstsq_laplace_factor_approx(model_approx, factor, delta=0.5, opt_kws=None):
    """
    """
    factor_approx = model_approx.factor_approximation(factor)
    opt = LeastSquaresOpt(factor_approx, **({} if (opt_kws is None) else opt_kws))
    (mode, covar, result) = opt.least_squares()
    message = (
        f"optimise.lsq_sq_laplace_factor_approx: nfev={result.nfev}, njev={result.njev}, optimality={result.optimality}, cost={result.cost}, status={result.status}, message={result.message}",
    )
    status = Status(result.success, message)
    model_dist = MeanField(
        {v: factor_approx.factor_dist[v].from_mode(mode[v], covar.get(v)) for v in mode}
    )
    (projection, status) = factor_approx.project(model_dist, delta=delta, status=status)
    return model_approx.project(projection, status=status)
