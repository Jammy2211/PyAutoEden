from copy import copy
from VIS_CTI_Autofit.VIS_CTI_Mapper.VIS_CTI_PriorModel import abstract
from VIS_CTI_Autofit.VIS_CTI_Mock.mock import MockSamples
from VIS_CTI_Autofit.VIS_CTI_NonLinear import abstract_search
from VIS_CTI_Autofit.VIS_CTI_NonLinear import VIS_CTI_Paths
from VIS_CTI_Autofit.VIS_CTI_NonLinear.result import Result
from VIS_CTI_Autofit.VIS_CTI_NonLinear.VIS_CTI_Grid.VIS_CTI_GridSearch import make_lists


class GridSearch:
    def __init__(self, step_size=0.5, name=None):
        self.step_size = step_size
        self.paths = paths.DirectoryPaths(name=name)

    @property
    def name(self):
        return self.paths.name

    def copy_with_paths(self, paths):
        search = copy(self)
        search.paths = paths
        return search

    def fit(self, model, analysis):
        best_likelihood = float("-inf")
        best_instance = None
        likelihoods = list()
        for list_ in make_lists(
            no_dimensions=model.prior_count, step_size=self.step_size
        ):
            instance = model.instance_from_unit_vector(list_)
            likelihood = analysis.log_likelihood_function(instance)
            likelihoods.append(likelihood)
            if likelihood > best_likelihood:
                best_likelihood = likelihood
                best_instance = instance
        return Result(
            samples=MockSamples(
                max_log_likelihood_instance=best_instance,
                log_likelihood_list=likelihoods,
                gaussian_tuples=None,
            ),
            model=model,
        )
