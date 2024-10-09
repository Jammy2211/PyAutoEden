from typing import Optional
import SLE_Model_Autofit as af
import SLE_Model_Autoarray as aa
from SLE_Model_Autolens import exc


class SubhaloAgg:
    def __init__(
        self, aggregator_grid_search, settings_inversion=None, use_preloaded_grid=True
    ):
        """
        Wraps a PyAutoFit aggregator in order to create generators of fits to imaging data, corresponding to the
        results of a non-linear search model-fit.
        """
        self.aggregator_grid_search = aggregator_grid_search
        self.settings_inversion = settings_inversion
        self.use_preloaded_grid = use_preloaded_grid
        if len(aggregator_grid_search) == 0:
            raise exc.AggregatorException(
                "There is no grid search of results in the aggregator."
            )
        elif len(aggregator_grid_search) > 1:
            raise exc.AggregatorException(
                "There is more than one grid search of results in the aggregator - please filter theaggregator."
            )

    @property
    def grid_search_result(self):
        return self.aggregator_grid_search[0]["result"]
