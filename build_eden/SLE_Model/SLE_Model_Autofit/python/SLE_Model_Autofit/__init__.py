import abc
import pickle

from SLE_Model_Autoconf.dictable import register_parser
from SLE_Model_Autofit.SLE_Model_NonLinear.SLE_Model_Grid.SLE_Model_GridSearch import (
    GridSearch as SearchGridSearch,
)
from SLE_Model_Autoconf import conf
from SLE_Model_Autofit import exc
from SLE_Model_Autofit import mock as m
from SLE_Model_Autofit.SLE_Model_Aggregator.base import AggBase
from SLE_Model_Autofit.SLE_Model_Database.SLE_Model_Aggregator.aggregator import (
    GridSearchAggregator,
)
from SLE_Model_Autofit.SLE_Model_Graphical.SLE_Model_ExpectationPropagation.history import (
    EPHistory,
)
from SLE_Model_Autofit.SLE_Model_Graphical.SLE_Model_Declarative.SLE_Model_Factor.analysis import (
    AnalysisFactor,
)
from SLE_Model_Autofit.SLE_Model_Graphical.SLE_Model_Declarative.collection import (
    FactorGraphModel,
)
from SLE_Model_Autofit.SLE_Model_Graphical.SLE_Model_Declarative.SLE_Model_Factor.hierarchical import (
    HierarchicalFactor,
)
from SLE_Model_Autofit.SLE_Model_Graphical.SLE_Model_Laplace import LaplaceOptimiser
from SLE_Model_Autofit.SLE_Model_NonLinear.SLE_Model_Grid.grid_list import GridList
from SLE_Model_Autofit.SLE_Model_NonLinear.SLE_Model_Samples.summary import (
    SamplesSummary,
)

from SLE_Model_Autofit.SLE_Model_NonLinear.SLE_Model_Samples import SamplesNest
from SLE_Model_Autofit.SLE_Model_NonLinear.SLE_Model_Samples import Samples
from SLE_Model_Autofit.SLE_Model_NonLinear.SLE_Model_Samples import SamplesPDF
from SLE_Model_Autofit.SLE_Model_NonLinear.SLE_Model_Samples import Sample
from SLE_Model_Autofit.SLE_Model_NonLinear.SLE_Model_Samples import load_from_table
from SLE_Model_Autofit.SLE_Model_NonLinear.SLE_Model_Samples import SamplesStored
from SLE_Model_Autofit.SLE_Model_Database.SLE_Model_Aggregator import Aggregator
from SLE_Model_Autofit.SLE_Model_Database.SLE_Model_Model import Fit
from SLE_Model_Autofit.SLE_Model_Database.SLE_Model_Aggregator import Query
from SLE_Model_Autofit.SLE_Model_Database.SLE_Model_Model.fit import Fit
from SLE_Model_Autofit.SLE_Model_Aggregator.search_output import SearchOutput
from SLE_Model_Autofit.SLE_Model_Mapper import SLE_Model_Prior
from SLE_Model_Autofit.SLE_Model_Mapper.model import AbstractModel
from SLE_Model_Autofit.SLE_Model_Mapper.model import ModelInstance
from SLE_Model_Autofit.SLE_Model_Mapper.model import ModelInstance as Instance
from SLE_Model_Autofit.SLE_Model_Mapper.model import path_instances_of_class
from SLE_Model_Autofit.SLE_Model_Mapper.model_mapper import ModelMapper
from SLE_Model_Autofit.SLE_Model_Mapper.model_mapper import ModelMapper as Mapper
from SLE_Model_Autofit.SLE_Model_Mapper.model_object import ModelObject
from SLE_Model_Autofit.SLE_Model_Mapper.operator import DiagonalMatrix
from SLE_Model_Autofit.SLE_Model_Mapper.SLE_Model_Prior.SLE_Model_Arithmetic.assertion import (
    ComparisonAssertion,
)
from SLE_Model_Autofit.SLE_Model_Mapper.SLE_Model_Prior.SLE_Model_Arithmetic.assertion import (
    ComparisonAssertion,
)
from SLE_Model_Autofit.SLE_Model_Mapper.SLE_Model_Prior.SLE_Model_Arithmetic.assertion import (
    GreaterThanLessThanAssertion,
)
from SLE_Model_Autofit.SLE_Model_Mapper.SLE_Model_Prior.SLE_Model_Arithmetic.assertion import (
    GreaterThanLessThanEqualAssertion,
)
from SLE_Model_Autofit.SLE_Model_Mapper.SLE_Model_Prior.deferred import DeferredArgument
from SLE_Model_Autofit.SLE_Model_Mapper.SLE_Model_Prior.deferred import DeferredInstance
from SLE_Model_Autofit.SLE_Model_Mapper.SLE_Model_Prior.width_modifier import (
    AbsoluteWidthModifier,
)
from SLE_Model_Autofit.SLE_Model_Mapper.SLE_Model_Prior.width_modifier import (
    RelativeWidthModifier,
)
from SLE_Model_Autofit.SLE_Model_Mapper.SLE_Model_Prior.width_modifier import (
    WidthModifier,
)
from SLE_Model_Autofit.SLE_Model_Mapper.SLE_Model_Prior import GaussianPrior
from SLE_Model_Autofit.SLE_Model_Mapper.SLE_Model_Prior import LogGaussianPrior
from SLE_Model_Autofit.SLE_Model_Mapper.SLE_Model_Prior import LogUniformPrior
from SLE_Model_Autofit.SLE_Model_Mapper.SLE_Model_Prior.abstract import Prior
from SLE_Model_Autofit.SLE_Model_Mapper.SLE_Model_Prior.tuple_prior import TuplePrior
from SLE_Model_Autofit.SLE_Model_Mapper.SLE_Model_Prior import UniformPrior
from SLE_Model_Autofit.SLE_Model_Mapper.SLE_Model_PriorModel.abstract import (
    AbstractPriorModel,
)
from SLE_Model_Autofit.SLE_Model_Mapper.SLE_Model_PriorModel.annotation import (
    AnnotationPriorModel,
)
from SLE_Model_Autofit.SLE_Model_Mapper.SLE_Model_PriorModel.collection import (
    Collection,
)
from SLE_Model_Autofit.SLE_Model_Mapper.SLE_Model_PriorModel.prior_model import Model
from SLE_Model_Autofit.SLE_Model_Mapper.SLE_Model_PriorModel.array import Array
from SLE_Model_Autofit.SLE_Model_NonLinear.SLE_Model_Search.abstract_search import (
    NonLinearSearch,
)
from SLE_Model_Autofit.SLE_Model_NonLinear.SLE_Model_Analysis.visualize import (
    Visualizer,
)
from SLE_Model_Autofit.SLE_Model_NonLinear.SLE_Model_Analysis.analysis import Analysis
from SLE_Model_Autofit.SLE_Model_NonLinear.SLE_Model_Analysis.combined import (
    CombinedAnalysis,
)
from SLE_Model_Autofit.SLE_Model_NonLinear.SLE_Model_Grid.SLE_Model_GridSearch import (
    GridSearchResult,
)
from SLE_Model_Autofit.SLE_Model_NonLinear.SLE_Model_Grid.SLE_Model_Sensitivity import (
    Sensitivity,
)
from SLE_Model_Autofit.SLE_Model_NonLinear.initializer import InitializerBall
from SLE_Model_Autofit.SLE_Model_NonLinear.initializer import InitializerPrior
from SLE_Model_Autofit.SLE_Model_NonLinear.initializer import InitializerParamBounds
from SLE_Model_Autofit.SLE_Model_NonLinear.initializer import (
    InitializerParamStartPoints,
)


from SLE_Model_Autofit.SLE_Model_NonLinear.SLE_Model_Search.SLE_Model_Nest.SLE_Model_Nautilus.search import (
    Nautilus,
)
from SLE_Model_Autofit.SLE_Model_NonLinear.SLE_Model_Search.SLE_Model_Nest.SLE_Model_Dynesty.SLE_Model_Search.dynamic import (
    DynestyDynamic,
)
from SLE_Model_Autofit.SLE_Model_NonLinear.SLE_Model_Search.SLE_Model_Nest.SLE_Model_Dynesty.SLE_Model_Search.static import (
    DynestyStatic,
)

from SLE_Model_Autofit.SLE_Model_NonLinear.SLE_Model_Search.SLE_Model_Mle.SLE_Model_Drawer.search import (
    Drawer,
)
from SLE_Model_Autofit.SLE_Model_NonLinear.SLE_Model_Search.SLE_Model_Mle.SLE_Model_Bfgs.search import (
    BFGS,
)
from SLE_Model_Autofit.SLE_Model_NonLinear.SLE_Model_Search.SLE_Model_Mle.SLE_Model_Bfgs.search import (
    LBFGS,
)
from SLE_Model_Autofit.SLE_Model_NonLinear.SLE_Model_Search.SLE_Model_Mle.SLE_Model_Pyswarms.SLE_Model_Search.globe import (
    PySwarmsGlobal,
)
from SLE_Model_Autofit.SLE_Model_NonLinear.SLE_Model_Search.SLE_Model_Mle.SLE_Model_Pyswarms.SLE_Model_Search.local import (
    PySwarmsLocal,
)
from SLE_Model_Autofit.SLE_Model_NonLinear.SLE_Model_Paths.abstract import AbstractPaths
from SLE_Model_Autofit.SLE_Model_NonLinear.SLE_Model_Paths import DirectoryPaths
from SLE_Model_Autofit.SLE_Model_NonLinear.SLE_Model_Paths import DatabasePaths
from SLE_Model_Autofit.SLE_Model_NonLinear.result import Result
from SLE_Model_Autofit.SLE_Model_NonLinear.result import ResultsCollection
from SLE_Model_Autofit.SLE_Model_NonLinear.settings import SettingsSearch
from SLE_Model_Autofit.SLE_Model_NonLinear.SLE_Model_Samples.pdf import marginalize
from SLE_Model_Autofit.SLE_Model_Example.model import Gaussian, Exponential
from SLE_Model_Autofit.SLE_Model_Text import formatter
from SLE_Model_Autofit.SLE_Model_Text import samples_text
from SLE_Model_Autofit.visualise import VisualiseGraph
from SLE_Model_Autofit.SLE_Model_Interpolator import (
    LinearInterpolator,
    SplineInterpolator,
    CovarianceInterpolator,
    LinearRelationship,
)
from SLE_Model_Autofit.SLE_Model_Tools import util
from SLE_Model_Autofit.SLE_Model_Mapper.SLE_Model_Prior.SLE_Model_Arithmetic.compound import (
    SumPrior as Add,
)
from SLE_Model_Autofit.SLE_Model_Mapper.SLE_Model_Prior.SLE_Model_Arithmetic.compound import (
    MultiplePrior as Multiply,
)
from SLE_Model_Autofit.SLE_Model_Mapper.SLE_Model_Prior.SLE_Model_Arithmetic.compound import (
    DivisionPrior as Divide,
)
from SLE_Model_Autofit.SLE_Model_Mapper.SLE_Model_Prior.SLE_Model_Arithmetic.compound import (
    ModPrior as Mod,
)
from SLE_Model_Autofit.SLE_Model_Mapper.SLE_Model_Prior.SLE_Model_Arithmetic.compound import (
    PowerPrior as Power,
)
from SLE_Model_Autofit.SLE_Model_Mapper.SLE_Model_Prior.SLE_Model_Arithmetic.compound import (
    AbsolutePrior as Abs,
)
from SLE_Model_Autofit.SLE_Model_Mapper.SLE_Model_Prior.SLE_Model_Arithmetic.compound import (
    Log,
)
from SLE_Model_Autofit.SLE_Model_Mapper.SLE_Model_Prior.SLE_Model_Arithmetic.compound import (
    Log10,
)
from SLE_Model_Autofit import SLE_Model_Example as ex
from SLE_Model_Autofit import SLE_Model_Database as db

for type_ in (
    "model",
    "collection",
    "tuple_prior",
    "dict",
    "instance",
    "Uniform",
    "LogUniform",
    "Gaussian",
    "LogGaussian",
    "compound",
):
    register_parser(type_, ModelObject.from_dict)


conf.instance.register(__file__)
__version__ = "2024.9.21.2"
