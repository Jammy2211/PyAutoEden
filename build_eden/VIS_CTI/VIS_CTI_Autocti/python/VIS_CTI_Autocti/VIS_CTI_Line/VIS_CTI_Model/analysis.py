from typing import List
from VIS_CTI_Autofit.VIS_CTI_NonLinear.VIS_CTI_Samples import PDFSamples
from VIS_CTI_Autofit.VIS_CTI_Mapper.VIS_CTI_PriorModel.collection import (
    CollectionPriorModel,
)
from VIS_CTI_Autofit.VIS_CTI_Mapper.model import ModelInstance
from VIS_CTI_Autofit.VIS_CTI_NonLinear.abstract_search import Analysis
from VIS_CTI_Autofit.VIS_CTI_NonLinear.VIS_CTI_Paths.directory import DirectoryPaths
from VIS_CTI_Autofit.VIS_CTI_NonLinear.abstract_search import NonLinearSearch
from VIS_CTI_Autocti.VIS_CTI_Line.dataset import DatasetLine
from VIS_CTI_Autocti.VIS_CTI_Line.fit import FitDatasetLine
from VIS_CTI_Autocti.VIS_CTI_Line.VIS_CTI_Model.visualizer import VisualizerDatasetLine
from VIS_CTI_Autocti.VIS_CTI_Model.result import ResultDataset
from VIS_CTI_Autocti.VIS_CTI_Line.VIS_CTI_Model.result import ResultDatasetLine
from VIS_CTI_Autocti.VIS_CTI_Model.settings import SettingsCTI1D
from VIS_CTI_Autocti.VIS_CTI_Util.clocker import Clocker1D


class AnalysisDatasetLine(Analysis):
    def __init__(
        self, dataset_line, clocker, settings_cti=SettingsCTI1D(), results=None
    ):
        super().__init__()
        self.dataset_line = dataset_line
        self.clocker = clocker
        self.settings_cti = settings_cti
        self.results = results

    def log_likelihood_function(self, instance):
        """
        Determine the fitness of a particular model

        Parameters
        ----------
        instance

        Returns
        -------
        fit: Fit
            How fit the model is and the model
        """
        self.settings_cti.check_total_density_within_range(traps=instance.cti.traps)
        fit = self.fit_from_instance(instance=instance)
        return fit.log_likelihood

    def fit_from_instance_and_dataset_line(self, instance, dataset_line):
        if instance.cti.traps is not None:
            traps = list(instance.cti.traps)
        else:
            traps = None
        post_cti_data = self.clocker.add_cti(
            data=dataset_line.pre_cti_data, trap_list=traps, ccd=instance.cti.ccd
        )
        return FitDatasetLine(dataset_line=dataset_line, post_cti_data=post_cti_data)

    def fit_from_instance(self, instance):
        return self.fit_from_instance_and_dataset_line(
            instance=instance, dataset_line=self.dataset_line
        )

    def visualize(self, paths, instance, during_analysis):
        fit = self.fit_from_instance(instance=instance)
        visualizer = VisualizerDatasetLine(visualize_path=paths.image_path)
        visualizer.visualize_dataset_line(dataset_line=self.dataset_line)
        visualizer.visualize_fit_line(fit=fit, during_analysis=during_analysis)

    def make_result(self, samples, model, search):
        return ResultDatasetLine(
            samples=samples, model=model, analysis=self, search=search
        )
