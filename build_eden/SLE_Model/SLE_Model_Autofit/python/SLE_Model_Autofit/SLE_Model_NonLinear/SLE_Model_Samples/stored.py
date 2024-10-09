from typing import List, Optional
from SLE_Model_Autofit.SLE_Model_Mapper.SLE_Model_PriorModel.abstract import (
    AbstractPriorModel,
)
from SLE_Model_Autofit.SLE_Model_NonLinear.SLE_Model_Samples.sample import Sample
from SLE_Model_Autofit.SLE_Model_NonLinear.SLE_Model_Samples.pdf import SamplesPDF


class SamplesStored(SamplesPDF):
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
