from abc import ABC, abstractmethod
from typing import List, cast, Optional, Union
from VIS_CTI_Autofit.VIS_CTI_Graphical.VIS_CTI_Declarative.VIS_CTI_Factor.prior import (
    PriorFactor,
)
from VIS_CTI_Autofit.VIS_CTI_Graphical.VIS_CTI_ExpectationPropagation.ep_mean_field import (
    EPMeanField,
)
from VIS_CTI_Autofit.VIS_CTI_Graphical.VIS_CTI_FactorGraphs.factor import Factor
from VIS_CTI_Autofit.VIS_CTI_Graphical.VIS_CTI_FactorGraphs.graph import FactorGraph
from VIS_CTI_Autofit.VIS_CTI_Mapper.VIS_CTI_Prior.abstract import Prior
from VIS_CTI_Autofit.VIS_CTI_Mapper.VIS_CTI_PriorModel.abstract import (
    AbstractPriorModel,
)
from VIS_CTI_Autofit.VIS_CTI_Mapper.variable import Variable
from VIS_CTI_Autofit.VIS_CTI_Text.formatter import TextFormatter


class DeclarativeGraphFormatter(ABC):
    def __init__(self, graph):
        self.graph = graph

    @abstractmethod
    def variable_formatter(self, variable):
        pass

    @property
    def info(self):
        """
        Describes the graph. Output in graph.info
        """
        prior_factor_info = """
""".join(
            map(self.info_for_prior_factor, self.graph.prior_factors)
        )
        analysis_factor_info = """

""".join(
            map(self.info_for_analysis_factor, self.graph.analysis_factors)
        )
        hierarchical_factor_info = """

""".join(
            map(self.info_for_hierarchical_factor, self.graph.hierarchical_factors)
        )
        string = f"""PriorFactors

{prior_factor_info}

AnalysisFactors

{analysis_factor_info}"""
        if len(self.graph.hierarchical_factors) > 0:
            string = f"""{string}

HierarchicalFactors

{hierarchical_factor_info}"""
        return string

    def _related_factor_names(self, variable, excluded_factor=None):
        """
        Create a comma separated string describing factor names associated with
        the variable.

        Hierarchical factors are grouped.

        Parameters
        ----------
        variable
            A variable in the graph
        excluded_factor
            A factor which should not be included. e.g. the factor
            for which the variable is being checked.

        Returns
        -------
        A string describing the other factor's relationship to the variable.
        """
        from VIS_CTI_Autofit.VIS_CTI_Graphical.VIS_CTI_Declarative.VIS_CTI_Factor.hierarchical import (
            _HierarchicalFactor,
        )

        related_factors = self.graph.related_factors(
            variable, excluded_factor=excluded_factor
        )
        names = set()
        for factor in related_factors:
            if isinstance(factor, _HierarchicalFactor):
                names.add(factor.distribution_model.name)
            else:
                names.add(factor.name_for_variable(variable))
        return ", ".join(sorted(names))

    def info_for_prior_factor(self, prior_factor):
        """
        A string describing a given PriorFactor in the context of this graph.
        """
        related_factor_names = self._related_factor_names(
            variable=prior_factor.variable, excluded_factor=prior_factor
        )
        formatter = TextFormatter()
        formatter.add(
            (f"{prior_factor.name} ({related_factor_names})",),
            self.variable_formatter(prior_factor.variable),
        )
        return formatter.text

    def info_for_analysis_factor(self, analysis_factor):
        """
        A string describing a given AnalysisFactor in the context of this graph.
        """
        model = analysis_factor.prior_model
        formatter = TextFormatter()
        for (path, prior) in model.path_instance_tuples_for_class(
            Prior, ignore_children=True
        ):
            name = path[(-1)]
            related_factor_names = self._related_factor_names(
                prior, excluded_factor=analysis_factor
            )
            if len(related_factor_names) > 0:
                name = f"{name} ({related_factor_names})"
            path = path[:(-1)] + (name,)
            formatter.add(path, self.variable_formatter(prior))
        return f"""{analysis_factor.name}

{formatter.text}"""

    def info_for_hierarchical_factor(self, hierarchical_factor):
        distribution_model_info = self.info_for_analysis_factor(hierarchical_factor)
        formatter = TextFormatter()
        for factor in hierarchical_factor.factors:
            related_factor_names = self._related_factor_names(
                variable=factor.variable, excluded_factor=factor
            )
            formatter.add(
                (related_factor_names,), self.variable_formatter(factor.variable)
            )
        return f"""{distribution_model_info}

Drawn Variables

{formatter.text}"""


class GraphInfoFormatter(DeclarativeGraphFormatter):
    """
    Formats a string that is output to graph.info
    """

    def variable_formatter(self, variable):
        """
        Returns a string description of the variable
        """
        return str(variable)


class ResultsFormatter(DeclarativeGraphFormatter):
    def __init__(self, graph, model_approx):
        """
        Formats a string that is output to graph.results

        Parameters
        ----------
        graph
            A factor graph comprising AnalysisFactors
        model_approx
            An approximation of the model at the point of output
        """
        self.model_approx = model_approx
        super().__init__(graph)

    def variable_formatter(self, variable):
        """
        Returns the mean value for the message corresponding to the
        variable
        """
        return self.model_approx.mean_field[variable].mean


class DeclarativeFactorGraph(FactorGraph):
    @property
    def analysis_factors(self):
        """
        Analysis factors associated with this graph.
        """
        from VIS_CTI_Autofit.VIS_CTI_Graphical.VIS_CTI_Declarative.VIS_CTI_Factor.analysis import (
            AnalysisFactor,
        )

        return cast(List[AnalysisFactor], self._factors_with_type(AnalysisFactor))

    @property
    def prior_factors(self):
        """
        Prior factors associated with this graph.
        """
        return cast(List[PriorFactor], self._factors_with_type(PriorFactor))

    @property
    def hierarchical_factors(self):
        """
        Prior factors associated with this graph.
        """
        from VIS_CTI_Autofit.VIS_CTI_Graphical.VIS_CTI_Declarative.VIS_CTI_Factor.hierarchical import (
            _HierarchicalFactor,
        )

        hierarchical_factor_set = set()
        for factor in self._factors_with_type(_HierarchicalFactor):
            hierarchical_factor_set.add(
                cast(_HierarchicalFactor, factor).distribution_model
            )
        return sorted(hierarchical_factor_set)

    @property
    def info(self):
        """
        Describes the graph. Output in graph.info
        """
        return GraphInfoFormatter(self).info

    def make_results_text(self, model_approx):
        """
        Generate text describing the graph w.r.t. a given model approximation
        """
        return ResultsFormatter(self, model_approx).info
