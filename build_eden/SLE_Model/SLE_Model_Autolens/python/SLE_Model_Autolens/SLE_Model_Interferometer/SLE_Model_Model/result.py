import SLE_Model_Autoarray as aa
from SLE_Model_Autogalaxy.SLE_Model_Analysis.SLE_Model_AdaptImages.adapt_images import (
    AdaptImages,
)
from SLE_Model_Autolens.SLE_Model_Lens.tracer import Tracer
from SLE_Model_Autolens.SLE_Model_Interferometer.fit_interferometer import (
    FitInterferometer,
)
from SLE_Model_Autolens.SLE_Model_Analysis.result import ResultDataset


class ResultInterferometer(ResultDataset):
    @property
    def max_log_likelihood_fit(self):
        """
        An instance of a `FitInterferometer` corresponding to the maximum log likelihood model inferred by the
        non-linear search.
        """
        return self.analysis.fit_from(instance=self.instance)

    @property
    def max_log_likelihood_tracer(self):
        """
        An instance of a `Tracer` corresponding to the maximum log likelihood model inferred by the non-linear search.

        The `Tracer` is computed from the `max_log_likelihood_fit`, as this ensures that all linear light profiles
        are converted to normal light profiles with their `intensity` values updated.
        """
        return (
            self.max_log_likelihood_fit.model_obj_linear_light_profiles_to_light_profiles
        )

    @property
    def real_space_mask(self):
        """
        The real space mask used by this model-fit.
        """
        return self.max_log_likelihood_fit.dataset.real_space_mask

    def adapt_images_from(self, use_model_images=False):
        """
        Returns the adapt-images which are used to make a pixelization's mesh and regularization adapt to the
        reconstructed galaxy's morphology.

        This can use either:

        - The model image of each galaxy in the best-fit model.
        - The subtracted image of each galaxy in the best-fit model, where the subtracted image is the dataset
          minus the model images of all other galaxies.

        In **PyAutoLens** these adapt images have had lensing calculations performed on them and therefore for source
        galaxies are their lensed model images in the image-plane.

        Parameters
        ----------
        use_model_images
            If True, the model images of the galaxies are used to create the adapt images. If False, the subtracted
            images of the galaxies are used.
        """
        return AdaptImages.from_result(result=self, use_model_images=True)
