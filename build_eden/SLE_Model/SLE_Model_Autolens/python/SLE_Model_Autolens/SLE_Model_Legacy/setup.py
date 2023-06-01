from typing import Optional
import SLE_Model_Autofit as af
import SLE_Model_Autogalaxy as ag


class SetupAdapt(ag.legacy.SetupAdapt):
    def __init__(
        self,
        hyper_galaxies_lens=False,
        hyper_galaxies_source=False,
        hyper_image_sky=None,
        hyper_background_noise=None,
        hyper_fixed_after_source=False,
        search_pix_cls=None,
        search_noise_cls=None,
        search_pix_dict=None,
        search_noise_dict=None,
        mesh_pixels_fixed=None,
    ):
        """
        The adapt setup of a pipeline, which controls how adaptive-features in PyAutoLens template pipelines run,
        for example controlling whether galaxies are used to scale the noise and the non-linear searches used
        in these searchs.

        Users can write their own pipelines which do not use or require the *SetupAdapt* class.

        Parameters
        ----------
        hyper_galaxies
            If a hyper-pipeline is being used, this determines if hyper-galaxy functionality is used to scale the
            noise-map of the dataset throughout the fitting.
        hyper_image_sky
            If a hyper-pipeline is being used, this determines if hyper-galaxy functionality is used include the
            image's background sky component in the model.
        hyper_background_noise
            If a hyper-pipeline is being used, this determines if hyper-galaxy functionality is used include the
            noise-map's background component in the model.
        hyper_fixed_after_source
            If `True`, the hyper parameters are fixed and not updated after a desnated pipeline in the analysis. For
            the `SLaM` pipelines this is after the `SourcePipeline`. This allow Bayesian model comparison to be
            performed objected between later searchs in a pipeline.
        search_pix_cls
            The non-linear search used by every adapt model-fit search.
        search_pix_dict
            The dictionary of search options for the adapt model-fit searches.
        """
        hyper_galaxies = hyper_galaxies_lens or hyper_galaxies_source
        super().__init__(
            hyper_galaxies=hyper_galaxies,
            hyper_image_sky=hyper_image_sky,
            hyper_background_noise=hyper_background_noise,
            search_pix_cls=search_pix_cls,
            search_noise_cls=search_noise_cls,
            search_pix_dict=search_pix_dict,
            search_noise_dict=search_noise_dict,
            mesh_pixels_fixed=mesh_pixels_fixed,
        )
        self.hyper_galaxies_lens = hyper_galaxies_lens
        self.hyper_galaxies_source = hyper_galaxies_source
        if self.hyper_galaxies_lens or self.hyper_galaxies_source:
            self.hyper_galaxy_names = []
        if self.hyper_galaxies_lens:
            self.hyper_galaxy_names.append("lens")
        if self.hyper_galaxies_source:
            self.hyper_galaxy_names.append("source")
        self.hyper_fixed_after_source = hyper_fixed_after_source

    def hyper_galaxy_lens_from(self, result, noise_factor_is_model=False):
        """
        Returns the `HyperGalaxy` `Model` from a previous pipeline or search of the lens galaxy in a template
        PyAutoLens pipeline.

        The `HyperGalaxy` is extracted from the `hyper` search of the previous pipeline, and by default has its
        parameters passed as instance's which are fixed in the next search.

        If `noise_factor_is_model` is `True` the `noise_factor` parameter of the `HyperGalaxy` is passed as a model and
        fitted for by the search. This is typically used when the lens model complexity is updated and it is possible
        that the noise-scaling performed in the previous search (using a simpler lens light model) over-scales the
        noise for the new more complex light profile.

        Parameters
        ----------
        index
            The index of the previous search the `HyperGalaxy` `Model` is passed from.
        noise_factor_is_model
            If `True` the `noise_factor` of the `HyperGalaxy` is passed as a `model`, else it is passed as an
            `instance`.

        Returns
        -------
        af.Model(g.HyperGalaxy)
            The hyper-galaxy that is passed to the next search.
        """
        if not self.hyper_galaxies_lens:
            return None
        if hasattr(result, "adapt"):
            return self.hyper_galaxy_via_galaxy_model_from(
                galaxy_model=result.adapt.model.galaxies.lens,
                galaxy_instance=result.adapt.instance.galaxies.lens,
                noise_factor_is_model=noise_factor_is_model,
            )
        return self.hyper_galaxy_via_galaxy_model_from(
            galaxy_model=result.model.galaxies.lens,
            galaxy_instance=result.instance.galaxies.lens,
            noise_factor_is_model=noise_factor_is_model,
        )

    def hyper_galaxy_source_from(self, result, noise_factor_is_model=False):
        """
        Returns the `HyperGalaxy` `Model` from a previous pipeline or search of the source galaxy in a template
        PyAutosource pipeline.

        The `HyperGalaxy` is extracted from the `hyper` search of the previous pipeline, and by default has its
        parameters passed as instance's which are fixed in the next search.

        If `noise_factor_is_model` is `True` the `noise_factor` parameter of the `HyperGalaxy` is passed as a model and
        fitted for by the search. This is typically used when the source model complexity is updated and it is possible
        that the noise-scaling performed in the previous search (using a simpler source light model) over-scales the
        noise for the new more complex light profile.

        Parameters
        ----------
        index
            The index of the previous search the `HyperGalaxy` `Model` is passed from.
        noise_factor_is_model
            If `True` the `noise_factor` of the `HyperGalaxy` is passed as a `model`, else it is passed as an
            `instance`.

        Returns
        -------
        af.Model(g.HyperGalaxy)
            The hyper-galaxy that is passed to the next search.
        """
        if not self.hyper_galaxies_source:
            return None
        if hasattr(result, "adapt"):
            return self.hyper_galaxy_via_galaxy_model_from(
                galaxy_model=result.adapt.model.galaxies.source,
                galaxy_instance=result.adapt.instance.galaxies.source,
                noise_factor_is_model=noise_factor_is_model,
            )
        return self.hyper_galaxy_via_galaxy_model_from(
            galaxy_model=result.model.galaxies.source,
            galaxy_instance=result.instance.galaxies.source,
            noise_factor_is_model=noise_factor_is_model,
        )

    def hyper_galaxy_via_galaxy_model_from(
        self, galaxy_model, galaxy_instance, noise_factor_is_model=False
    ):
        hyper_galaxy = af.Model(ag.HyperGalaxy)
        if galaxy_model.hyper_galaxy is None:
            return None
        if not noise_factor_is_model:
            hyper_galaxy.noise_factor = galaxy_instance.hyper_galaxy.noise_factor
        else:
            hyper_galaxy.noise_factor = af.LogUniformPrior(
                lower_limit=0.0001,
                upper_limit=(2.0 * galaxy_instance.hyper_galaxy.noise_factor),
            )
        hyper_galaxy.contribution_factor = (
            galaxy_instance.hyper_galaxy.contribution_factor
        )
        hyper_galaxy.noise_power = galaxy_instance.hyper_galaxy.noise_power
        return hyper_galaxy
