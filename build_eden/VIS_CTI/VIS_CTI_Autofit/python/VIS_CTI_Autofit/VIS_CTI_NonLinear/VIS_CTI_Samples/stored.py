from typing import List, Optional
from VIS_CTI_Autofit.VIS_CTI_Mapper.VIS_CTI_PriorModel.abstract import (
    AbstractPriorModel,
)
from VIS_CTI_Autofit.VIS_CTI_NonLinear.VIS_CTI_Samples.sample import Sample
from VIS_CTI_Autofit.VIS_CTI_NonLinear.VIS_CTI_Samples.pdf import PDFSamples


class StoredSamples(PDFSamples):
    def __init__(self, model, sample_list, unconverged_sample_size=100, time=None):
        """
        The `Samples` of a non-linear search, specifically the samples of a `NonLinearSearch` which maps out the
        posterior of parameter space and thus does provide information on parameter errors.

        Parameters
        ----------
        model : af.ModelMapper
            Maps input vectors of unit parameter values to physical values and model instances via priors.
        """
        super().__init__(model=model, sample_list=sample_list, time=time)
        self._unconverged_sample_size = int(unconverged_sample_size)
