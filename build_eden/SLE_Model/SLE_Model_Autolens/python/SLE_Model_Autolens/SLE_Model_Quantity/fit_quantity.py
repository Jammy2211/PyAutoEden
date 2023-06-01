import SLE_Model_Autoarray as aa
import SLE_Model_Autogalaxy as ag
from SLE_Model_Autogalaxy.SLE_Model_Quantity.dataset_quantity import DatasetQuantity
from SLE_Model_Autolens.SLE_Model_Lens.ray_tracing import Tracer


class FitQuantity(ag.FitQuantity):
    def __init__(self, dataset, tracer, func_str):
        """
        Fits a `DatasetQuantity` object with model data.

        This is used to fit a quantity (e.g. a convergence, deflection angles), from a `Tracer`, to the same quantity
        derived from another of that object.

        For example, we may have the 2D convergence of a power-law mass profile and wish to determine how closely the
        2D convergence of an nfw mass profile's matches it. The `FitQuantity` can fit the two, where a noise-map
        is associated with the quantity's dataset such that figure of merits like a chi-squared and log likelihood
        can be computed.

        This is ultimately used in the `AnalysisQuantity` class to perform model-fitting of quantities of different
        mass profiles, light profiles, galaxies, etc.

        Parameters
        ----------
        dataset
            The quantity that is to be fitted, which has a noise-map associated it with for computing goodness-of-fit
            metrics.
        tracer
            The tracer of galaxies whose model quantities are used to fit the imaging data.
        func_str
            A string giving the name of the method of the input `Plane` used to compute the quantity that fits
            the dataset.
        """
        super().__init__(dataset=dataset, light_mass_obj=tracer, func_str=func_str)

    @property
    def tracer(self):
        return self.light_mass_obj
