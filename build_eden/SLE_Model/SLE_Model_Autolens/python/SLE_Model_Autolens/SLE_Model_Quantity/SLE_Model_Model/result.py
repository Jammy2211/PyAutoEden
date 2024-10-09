import SLE_Model_Autoarray as aa
import SLE_Model_Autogalaxy as ag
from SLE_Model_Autolens.SLE_Model_Lens.tracer import Tracer
from SLE_Model_Autolens.SLE_Model_Analysis.result import Result


class ResultQuantity(Result):
    """
    After the non-linear search of a fit to a quantity dataset is complete it creates this `ResultQuantity` object,
    which includes:

    - The samples of the non-linear search (E.g. MCMC chains, nested sampling samples) which are used to compute
    the maximum likelihood model, posteriors and other properties.

    - The model used to fit the data, which uses the samples to create specific instances of the model (e.g.
    an instance of the maximum log likelihood model).

    - The non-linear search used to perform the model fit.

    This class contains a number of methods which use the above objects to create the max log likelihood `Galaxies`,
    `FitQuantity`, etc.

    Parameters
    ----------
    samples
        A PyAutoFit object which contains the samples of the non-linear search, for example the chains of an MCMC
        run of samples of the nested sampler.
    model
        The model object, which includes model components representing the galaxies that are fitted to
        the imaging data.
    search
        The non-linear search used to perform this model-fit.

    Returns
    -------
    ResultQuantity
        The result of fitting the model to the imaging dataset, via a non-linear search.
    """

    @property
    def grid(self):
        """
        The masked 2D grid used by the dataset in the model-fit.
        """
        return self.analysis.dataset.grids.uniform

    @property
    def max_log_likelihood_tracer(self):
        """
        An instance of a `Tracer` corresponding to the maximum log likelihood model inferred by the non-linear search.

        If a dataset is fitted the adapt images of the adapt image must first be associated with each galaxy.
        """
        return self.analysis.tracer_via_instance_from(instance=self.instance)

    @property
    def max_log_likelihood_fit(self):
        """
        An instance of a `FitQuantity` corresponding to the maximum log likelihood model inferred by the non-linear
        search.
        """
        return self.analysis.fit_quantity_for_instance(instance=self.instance)
