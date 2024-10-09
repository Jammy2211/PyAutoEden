from abc import ABC, abstractmethod
from itertools import count, chain
from typing import List, Tuple, Dict, Set, Optional, Collection, Any, TYPE_CHECKING
import numpy as np
from SLE_Model_Autoconf import cached_property
from SLE_Model_Autofit.SLE_Model_Graphical.utils import (
    FlattenArrays,
    nested_filter,
    nested_update,
    nested_zip,
    nested_set,
    nested_map,
    nested_items,
    is_variable,
    Status,
)
from SLE_Model_Autofit.SLE_Model_Mapper.variable import (
    Variable,
    Plate,
    FactorValue,
    VariableData,
)

if TYPE_CHECKING:
    from SLE_Model_Autofit.SLE_Model_Graphical.mean_field import MeanField
    from SLE_Model_Autofit.SLE_Model_Graphical.SLE_Model_ExpectationPropagation import (
        EPMeanField,
    )
Protocol = ABC
Value = Dict[(Variable, np.ndarray)]
GradientValue = VariableData
HessianValue = Any


class FactorInterface(Protocol):
    def __call__(self, values):
        pass


class FactorGradientInterface(Protocol):
    def __call__(self, values):
        pass


class AbstractNode(ABC):
    _plates: Tuple[(Plate, ...)] = ()
    _factor: callable = None
    label = None
    _id = count()
    eps = 1e-06

    def __init__(self, plates=(), factor_out=FactorValue, name="", **kwargs: Variable):
        """
        A node in a factor graph

        Parameters
        ----------
        args
            Positional arguments passed to the factor
        kwargs
            Key word arguments passed to the value
        """
        self._plates = plates
        self._kwargs = kwargs
        self._name = name or (type(self).__name__ + str(tuple(self.variables)))
        self._factor_out = factor_out
        self.id = next(self._id)

    def resolve_variable_dict(self, values):
        return {
            self.variable_name_kw[v.name]: x
            for (v, x) in values.items()
            if (v.name in self.variable_name_kw)
        }

    def resolve_args(self, values):
        return nested_update(self.args, values)

    @cached_property
    def fixed_values(self):
        return VariableData()

    @cached_property
    def variables(self):
        """
        Dictionary mapping the names of variables to those variables
        """
        return frozenset(self.flat_args)

    @property
    def free_variables(self):
        return self.variables - self.fixed_values.keys()

    @property
    def kwargs(self):
        return self._kwargs

    @kwargs.setter
    def kwargs(self, kwargs):
        del self.variables
        del self.name_variable_dict
        del self.variable_name_dict
        self._kwargs = kwargs

    @property
    def args(self):
        return tuple(self.kwargs.values())

    @property
    def arg_names(self):
        return tuple(self.kwargs)

    @property
    def flat_args(self):
        return tuple((x for (x,) in nested_zip(self._kwargs)))

    @property
    def factor_out(self):
        return self._factor_out

    @factor_out.setter
    def factor_out(self, factor_out):
        del self.deterministic_variables
        self._factor_out = factor_out

    @property
    def n_args(self):
        return len(self.args)

    @cached_property
    def name_variable_dict(self):
        return {variable.name: variable for variable in self.variables}

    @cached_property
    def variable_name_dict(self):
        return {variable.name: kw for (kw, variable) in self._kwargs.items()}

    @cached_property
    def deterministic_variables(self):
        deterministic_variables = set(
            (v for (v,) in nested_filter(is_variable, self.factor_out))
        )
        deterministic_variables.discard(FactorValue)
        return frozenset(deterministic_variables)

    @property
    def plates(self):
        return self._plates

    @cached_property
    def sorted_plates(self):
        """
        A tuple of the set of all plates in this graph, ordered by id
        """
        return tuple(
            sorted(
                set(
                    (
                        plate
                        for variable in self.all_variables
                        for plate in variable.plates
                    )
                )
            )
        )

    def __getitem__(self, item):
        try:
            return self._kwargs[item]
        except KeyError as e:
            for variable in self.all_variables:
                if variable.name == item:
                    return variable
            raise AttributeError(f"No attribute {item}") from e

    @property
    def name(self):
        """
        A name for this object
        """
        return self._name

    @property
    def call_signature(self):
        """
        The apparent signature of this object
        """
        call_str = ", ".join(map("{0}={0}".format, self.kwarg_names))
        call_sig = f"{self.name}({call_str})"
        return call_sig

    @property
    def kwarg_names(self):
        """
        The names of the variables passed as keyword arguments
        """
        return [arg.name for arg in self._kwargs.values()]

    @property
    def all_variables(self):
        """
        A dictionary of variables associated with this node
        """
        return self.variables.union(self.deterministic_variables)

    @property
    def ndim(self):
        """
        The number of plates contained within this graph's variables

        That is, the total dimensions of those variables.
        """
        return len(self.sorted_plates)

    def _match_plates(self, plates):
        """
        Find indices plates from some factor in the collection of
        plates associated with this node.

        Parameters
        ----------
        plates
            Plates from some other node

        Returns
        -------
        An array of plate indices
        """
        return np.array([self.plates.index(p) for p in plates], dtype=int)

    @abstractmethod
    def __call__(self, **kwargs):
        pass

    @property
    def _unique_representation(self):
        return (
            self._factor,
            self.arg_names,
            self.flat_args,
            self.deterministic_variables,
        )

    def __hash__(self):
        return hash(self._unique_representation)

    def __eq__(self, other):
        if isinstance(other, type(self)):
            return self._unique_representation == other._unique_representation
        return False

    def _factor_args(self, *args):
        return self._factor(**dict(zip(self.arg_names, args)))

    def _numerical_factor_jacobian(self, *args, eps: Optional[float] = None, **kwargs):
        """Calculates the dense numerical jacobian matrix with respect to
        the input arguments, broadly speaking, the following should return the
        same values (within numerical precision of the finite differences)

        factor._numerical_factor_jacobian(*args)

        factor._factor(*args), jax.jacobian(factor._factor, range(len(args)))(*args)
        """
        eps = eps or self.eps
        args = nested_map(
            (lambda _, val: np.array(val, dtype=np.float64)), self.args, args
        )
        raw_fval0 = self._factor_args(*args)
        fval0 = self._factor_value(raw_fval0).to_dict()
        jac = {
            v0: nested_map(
                (lambda _, v: np.empty_like(val, shape=(np.shape(val) + np.shape(v)))),
                self.args,
                args,
            )
            for (v0, val) in fval0.items()
        }
        for (ks, _, val) in nested_items(self.args, args):
            with np.nditer(val, op_flags=["readwrite"], flags=["multi_index"]) as it:
                for x_i in it:
                    val[it.multi_index] += eps
                    fval1 = self._factor_value(self._factor_args(*args)).to_dict()
                    jac_v1_i = (fval1 - fval0) / eps
                    x_i -= eps
                    indexes = (Ellipsis,) + it.multi_index
                    for (v0, jac_v0v_i) in jac_v1_i.items():
                        key_path = (v0, *ks, indexes)
                        nested_set(jac, key_path, jac_v0v_i)
        jac_out = nested_update(self.factor_out, jac)
        return (raw_fval0, jac_out)

    def numerical_func_jacobian(self, values, **kwargs):
        args = self.resolve_args(values)
        (raw_fval, raw_jac) = self._numerical_factor_jacobian(*args, **kwargs)
        fval = self._factor_value(raw_fval)
        jvp = self._jac_out_to_jvp(raw_jac, values=fval.to_dict().merge(values))
        return (fval, jvp)

    def jacobian(self, values, **kwargs):
        return self.func_jacobian(values, **kwargs)[1]

    def func_gradient(self, values):
        (fval, fjac) = self.func_jacobian(values)
        return (fval, fjac.grad())

    def flatten(self, param_shapes):
        return FlattenedNode(self, param_shapes)


class AbstractFactor(AbstractNode, ABC):
    def __lt__(self, other):
        return self.name < other.name

    def __gt__(self, other):
        return self.name > other.name

    def __mul__(self, other):
        """
        When two factors are multiplied together this creates a graph
        """
        from SLE_Model_Autofit.SLE_Model_Graphical.SLE_Model_FactorGraphs.graph import (
            FactorGraph,
        )

        return FactorGraph([self]) * other

    @property
    def _kwargs_dims(self):
        """
        The number of plates for each keyword argument variable
        """
        return {key: len(value) for (key, value) in self._kwargs.items()}

    @cached_property
    def _variable_plates(self):
        """
        Maps the name of each variable to the indices of its plates
        within this node
        """
        return {
            variable: self._match_plates(variable.plates)
            for variable in self.all_variables
        }

    @property
    def n_deterministic(self):
        """
        How many deterministic variables are there associated with this node?
        """
        return len(self._deterministic_variables)

    def _set_factor(self, factor):
        self._factor = factor
        self._has_exact_projection = getattr(factor, "has_exact_projection", None)
        self._calc_exact_projection = getattr(factor, "calc_exact_projection", None)
        self._calc_exact_update = getattr(factor, "calc_exact_update", None)

    def resolve_args_and_out(self, values):
        if self.factor_out == FactorValue:
            return self.resolve_args(values)
        else:
            return chain(
                self.resolve_args(values), (nested_update(self.factor_out, values),)
            )

    def has_exact_projection(self, mean_field):
        if self._has_exact_projection:
            return self._has_exact_projection(*self.resolve_args_and_out(mean_field))
        return False

    def calc_exact_projection(self, mean_field):
        if self._calc_exact_projection:
            from SLE_Model_Autofit.SLE_Model_Graphical.mean_field import MeanField

            projection = self._calc_exact_projection(
                *self.resolve_args_and_out(mean_field)
            )
            return MeanField(
                nested_filter(is_variable, (self.args + (self.factor_out,)), projection)
            )
        else:
            raise NotImplementedError

    def calc_exact_update(self, mean_field):
        if self._calc_exact_update:
            from SLE_Model_Autofit.SLE_Model_Graphical.mean_field import MeanField

            projection = self._calc_exact_update(*self.resolve_args_and_out(mean_field))
            return MeanField(
                nested_filter(is_variable, (self.args + (self.factor_out,)), projection)
            )
        else:
            raise NotImplementedError

    def name_for_variable(self, variable):
        return self.name

    @property
    def info(self):
        return repr(self)

    def __repr__(self):
        args = ", ".join(map(str, self.args))
        clsname = type(self).__name__
        if self.deterministic_variables:
            args += f", factor_out={self.factor_out}"
        return f"{clsname}({self.name}, {args})"

    def make_results_text(self, model_approx):
        """
        Create a string describing the posterior values after this factor
        during or after an EPOptimisation.
        Parameters
        ----------
        model_approx: EPMeanField
        Returns
        -------
        A string containing the name of this factor with the names and
        values of each associated variable in the mean field.
        """
        string = """
""".join(
            (
                f"{variable} = {model_approx.mean_field[variable].mean}"
                for variable in self.variables
            )
        )
        return f"""{self.name}

{string}"""


class FlattenedNode:
    def __init__(self, node, param_shapes):
        self.node = node
        self.param_shapes = param_shapes

    def flatten(self, values):
        return self.param_shapes.flatten(values)

    def unflatten(self, x0):
        return self.param_shapes.unflatten(x0)

    def __call__(self, x):
        values = self.unflatten(x)
        return self.node(values)

    def func_jacobian(self, x):
        values = self.unflatten(x)
        (fval, jval) = self.node.func_jacobian(values)
        grad = self.flatten(jval)
        return (fval, grad)

    def func_jacobian_hessian(self, x):
        values = self.unflatten(x)
        (fval, jval, hval) = self.node.func_jacobian_hessian(values)
        grad = self.flatten(jval)
        hess = self.param_shapes.flatten2d(hval)
        return (fval, grad, hess)

    def jacobian(self, x):
        return self.func_jacobian(x)[1]

    def hessian(self, x):
        return self.func_jacobian_hessian(x)[1]

    def __getattribute__(self, name):
        try:
            return super().__getattribute__(name)
        except AttributeError:
            return getattr(self.node, name)
