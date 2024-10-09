from __future__ import annotations
from typing import TYPE_CHECKING, Dict, List

if TYPE_CHECKING:
    from SLE_Model_Autogalaxy import SLE_Model_Mock
import SLE_Model_Autofit as af
import SLE_Model_Autogalaxy as ag


class MockResult(af.m.MockResult):
    def __init__(
        self,
        samples=None,
        instance=None,
        model=None,
        analysis=None,
        search=None,
        max_log_likelihood_galaxies=None,
        max_log_likelihood_tracer=None,
    ):
        super().__init__(
            samples=samples,
            instance=instance,
            model=model,
            analysis=analysis,
            search=search,
        )
        self.max_log_likelihood_galaxies = max_log_likelihood_galaxies
        self.max_log_likelihood_tracer = max_log_likelihood_tracer

    @property
    def last(self):
        return self
