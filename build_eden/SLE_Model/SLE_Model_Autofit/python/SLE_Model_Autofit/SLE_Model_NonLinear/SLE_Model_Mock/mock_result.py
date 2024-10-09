from SLE_Model_Autofit.SLE_Model_Mapper.model import ModelInstance
from SLE_Model_Autofit.SLE_Model_Mapper.model_mapper import ModelMapper
from SLE_Model_Autofit.SLE_Model_NonLinear.result import Result
from SLE_Model_Autofit.SLE_Model_NonLinear.SLE_Model_Mock.mock_samples import (
    MockSamples,
)


class MockResult(Result):
    def __init__(
        self, samples=None, instance=None, model=None, analysis=None, search=None
    ):
        super().__init__(samples, model, search)
        self._instance = instance or ModelInstance()
        self.model = model or ModelMapper()
        self._samples = samples or MockSamples(
            max_log_likelihood_instance=self.instance
        )
        self.gaussian_tuples = None
        self.analysis = analysis
        self.search = search
        self.model = model

    def model_absolute(self, absolute):
        return self.model

    def model_relative(self, relative):
        return self.model

    @property
    def last(self):
        return self


class MockResultGrid(Result):
    def __init__(self, log_likelihood):
        super().__init__(None, None)
        self._log_likelihood = log_likelihood
        self.model = log_likelihood

    @property
    def log_likelihood(self):
        return self._log_likelihood
