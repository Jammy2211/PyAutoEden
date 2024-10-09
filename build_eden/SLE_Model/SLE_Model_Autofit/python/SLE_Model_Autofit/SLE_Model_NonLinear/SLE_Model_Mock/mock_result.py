from SLE_Model_Autofit.SLE_Model_Mapper.model import ModelInstance
from SLE_Model_Autofit.SLE_Model_Mapper.model_mapper import ModelMapper
from SLE_Model_Autofit.SLE_Model_NonLinear.result import Result
from SLE_Model_Autofit.SLE_Model_NonLinear.SLE_Model_Mock.mock_samples_summary import (
    MockSamplesSummary,
)
from SLE_Model_Autofit.SLE_Model_NonLinear.SLE_Model_Mock.mock_samples import (
    MockSamples,
)


class MockResult(Result):
    def __init__(
        self,
        samples_summary=None,
        paths=None,
        samples=None,
        instance=None,
        analysis=None,
        search=None,
        model=None,
    ):
        super().__init__(
            samples_summary=(
                samples_summary or MockSamplesSummary(model=(model or ModelMapper()))
            ),
            paths=paths,
            samples=samples,
            search_internal=None,
        )
        self._instance = instance or ModelInstance()
        self._samples = samples or MockSamples(model=(model or ModelMapper()))
        self.prior_means = None
        self.analysis = analysis
        self.search = search
        self.model = model

    def model_absolute(self, a):
        try:
            return self.samples_summary.model_absolute(a)
        except AttributeError:
            return self.model

    def model_relative(self, r):
        try:
            return self.samples_summary.model_relative(r)
        except AttributeError:
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

    @property
    def best_model(self):
        return self.model
