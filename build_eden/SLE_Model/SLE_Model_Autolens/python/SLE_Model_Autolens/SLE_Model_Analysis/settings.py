from typing import Optional


class SettingsLens:
    def __init__(
        self,
        stochastic_likelihood_resamples=None,
        stochastic_samples=250,
        stochastic_histogram_bins=10,
    ):
        self.stochastic_likelihood_resamples = stochastic_likelihood_resamples
        self.stochastic_samples = stochastic_samples
        self.stochastic_histogram_bins = stochastic_histogram_bins
