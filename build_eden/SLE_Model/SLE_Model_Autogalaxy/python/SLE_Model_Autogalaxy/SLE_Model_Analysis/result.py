import copy
import numpy as np
from typing import Dict, List, Tuple, Type, Union
from SLE_Model_Autoconf import conf
import SLE_Model_Autofit as af
import SLE_Model_Autoarray as aa
from SLE_Model_Autogalaxy.SLE_Model_Galaxy.galaxy import Galaxy
from SLE_Model_Autogalaxy.SLE_Model_Plane.plane import Plane


class Result(af.Result):
    def __init__(self, samples, model, analysis):
        """
        After the non-linear search of a fit to a dataset is complete it creates a `Result` object which includes:

        - The samples of the non-linear search (E.g. MCMC chains, nested sampling samples) which are used to compute
          the maximum likelihood model, posteriors and other properties.

        - The model used to fit the data, which uses the samples to create specific instances of the model (e.g.
          an instance of the maximum log likelihood model).

        - The non-linear search used to perform the model fit.

        This class contains a number of methods which use the above objects to create the max log likelihood `Plane`,
        `FitIamging`, adapt-galaxy images,etc.

        Parameters
        ----------
        samples
            A PyAutoFit object which contains the samples of the non-linear search, for example the chains of an MCMC
            run of samples of the nested sampler.
        model
            The PyAutoFit model object, which includes model components representing the galaxies that are fitted to
            the imaging data.
        analysis
            The `Analysis` object that was used to perform the model-fit from which this result is inferred.
        search
            The non-linear search used to perform this model-fit.

        Returns
        -------
        ResultImaging
            The result of fitting the model to the imaging dataset, via a non-linear search.
        """
        super().__init__(samples=samples, model=model)
        self.analysis = analysis
        self.__instance = None

    @property
    def instance_copy(self):
        """
        This is neccessary because the attributes of the `instance` are altered in the fit function, when linear
        light profiles are converted to standard light profile.

        This impacts autofit prior passing.

        Returns
        -------
        A deep copy of the instance of the max log likelihood result.
        """
        if self.__instance is None:
            self.__instance = copy.deepcopy(self.instance)
        return self.__instance

    @property
    def max_log_likelihood_plane(self):
        """
        An instance of a `Plane` corresponding to the maximum log likelihood model inferred by the non-linear search.
        """
        instance = self.analysis.instance_with_associated_adapt_images_from(
            instance=self.instance_copy
        )
        return self.analysis.plane_via_instance_from(instance=instance)

    @property
    def path_galaxy_tuples(self):
        """
        Tuples associating the names of galaxies with instances from the best fit
        """
        return self.instance_copy.path_instance_tuples_for_class(cls=Galaxy)


class ResultDataset(Result):
    def cls_list_from(self, cls):
        """
        A list of all pixelization classes used by the model-fit.
        """
        return self.max_log_likelihood_plane.cls_list_from(cls=cls)

    @property
    def mask(self):
        """
        The 2D mask applied to the dataset for the model-fit.
        """
        return self.max_log_likelihood_fit.mask

    @property
    def grid(self):
        """
        The masked 2D grid used by the dataset in the model-fit.
        """
        return self.analysis.dataset.grid

    @property
    def dataset(self):
        """
        The dataset that was fitted by the model-fit.
        """
        return self.max_log_likelihood_fit.dataset

    def image_for_galaxy(self, galaxy):
        """
        Given an instance of a `Galaxy` object, return an image of the galaxy via the maximum log likelihood fit.

        This image is extracted via the fit's `galaxy_model_image_dict`, which is necessary to make it straight
        forward to use the image as hyper-images.

        Parameters
        ----------
        galaxy
            A galaxy used by the model-fit.

        Returns
        -------
        ndarray or None
            A numpy arrays giving the model image of that galaxy.
        """
        return self.max_log_likelihood_fit.galaxy_model_image_dict[galaxy]

    @property
    def image_galaxy_dict(self):
        """
        A dictionary associating galaxy names with model images of those galaxies.

        This is used for creating the adapt-dataset used by Analysis objects to adapt aspects of a model to the dataset
        being fitted.
        """
        return {
            galaxy_path: self.image_for_galaxy(galaxy)
            for (galaxy_path, galaxy) in self.path_galaxy_tuples
        }

    @property
    def adapt_galaxy_image_path_dict(self):
        """
        A dictionary associating 1D galaxy images with their names.
        """
        adapt_minimum_percent = conf.instance["general"]["adapt"][
            "adapt_minimum_percent"
        ]
        adapt_galaxy_image_path_dict = {}
        for (path, galaxy) in self.path_galaxy_tuples:
            galaxy_image = self.image_galaxy_dict[path]
            if not np.all((galaxy_image == 0)):
                minimum_galaxy_value = adapt_minimum_percent * max(galaxy_image)
                galaxy_image[
                    (galaxy_image < minimum_galaxy_value)
                ] = minimum_galaxy_value
            adapt_galaxy_image_path_dict[path] = galaxy_image
        return adapt_galaxy_image_path_dict

    @property
    def adapt_model_image(self):
        """
        The adapt image used by Analysis objects to adapt aspects of a model to the dataset being fitted.

        The adapt image is the sum of the galaxy image of every individual galaxy.
        """
        adapt_model_image = aa.Array2D(
            values=np.zeros(self.mask.derive_mask.sub_1.pixels_in_mask),
            mask=self.mask.derive_mask.sub_1,
        )
        for (path, galaxy) in self.path_galaxy_tuples:
            adapt_model_image += self.adapt_galaxy_image_path_dict[path]
        return adapt_model_image