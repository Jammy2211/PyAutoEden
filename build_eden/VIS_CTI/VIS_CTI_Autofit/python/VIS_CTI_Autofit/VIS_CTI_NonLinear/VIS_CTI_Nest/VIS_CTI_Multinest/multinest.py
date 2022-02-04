from os import path
from typing import Optional
from VIS_CTI_Autoconf import conf
from VIS_CTI_Autofit.VIS_CTI_Database.sqlalchemy_ import sa
from VIS_CTI_Autofit.VIS_CTI_Mapper.VIS_CTI_PriorModel.abstract import (
    AbstractPriorModel,
)
from VIS_CTI_Autofit.VIS_CTI_NonLinear import abstract_search
from VIS_CTI_Autofit.VIS_CTI_NonLinear import result as res
from VIS_CTI_Autofit.VIS_CTI_NonLinear.abstract_search import PriorPasser
from VIS_CTI_Autofit.VIS_CTI_NonLinear.VIS_CTI_Nest import abstract_nest
from VIS_CTI_Autofit.VIS_CTI_NonLinear.VIS_CTI_Nest.VIS_CTI_Multinest.samples import (
    MultiNestSamples,
)


class MultiNest(abstract_nest.AbstractNest):
    __identifier_fields__ = (
        "n_live_points",
        "sampling_efficiency",
        "const_efficiency_mode",
        "importance_nested_sampling",
        "max_modes",
        "mode_tolerance",
    )

    def __init__(
        self,
        name=None,
        path_prefix=None,
        unique_tag=None,
        prior_passer=None,
        session=None,
        **kwargs
    ):
        """
        A MultiNest non-linear search.

        For a full description of MultiNest and its Python wrapper PyMultiNest, checkout its Github and documentation
        webpages:

        https://github.com/JohannesBuchner/MultiNest
        https://github.com/JohannesBuchner/PyMultiNest
        http://johannesbuchner.github.io/PyMultiNest/index.html#

        Parameters
        ----------
        name
            The name of the search, controlling the last folder results are output.
        path_prefix
            The path of folders prefixing the name folder where results are output.
        unique_tag
            The name of a unique tag for this model-fit, which will be given a unique entry in the sqlite database
            and also acts as the folder after the path prefix and before the search name.
        prior_passer
            Controls how priors are passed from the results of this `NonLinearSearch` to a subsequent non-linear search.
        session
            An SQLalchemy session instance so the results of the model-fit are written to an SQLite database.
        """
        super().__init__(
            name=name,
            path_prefix=path_prefix,
            unique_tag=unique_tag,
            prior_passer=prior_passer,
            session=session,
            **kwargs
        )
        self.logger.debug("Creating MultiNest Search")

    class Fitness(abstract_nest.AbstractNest.Fitness):
        def __init__(
            self,
            paths,
            model,
            analysis,
            samples_from_model,
            stagger_resampling_likelihood,
            log_likelihood_cap=None,
        ):
            super().__init__(
                model=model,
                analysis=analysis,
                samples_from_model=samples_from_model,
                stagger_resampling_likelihood=stagger_resampling_likelihood,
                log_likelihood_cap=log_likelihood_cap,
                paths=paths,
            )
            should_update_sym = conf.instance["non_linear"]["nest"]["MultiNest"][
                "updates"
            ]["should_update_sym"]
            self.should_update_sym = abstract_search.IntervalCounter(should_update_sym)

        def fit_instance(self, instance):
            if self.should_update_sym():
                self.paths.copy_from_sym()
            log_likelihood = self.analysis.log_likelihood_function(instance=instance)
            if self.log_likelihood_cap is not None:
                if log_likelihood > self.log_likelihood_cap:
                    log_likelihood = self.log_likelihood_cap
            return log_likelihood

    def _fit(self, model, analysis, log_likelihood_cap=None):
        """
        Fit a model using MultiNest and the Analysis class which contains the data and returns the log likelihood from
        instances of the model, which the `NonLinearSearch` seeks to maximize.

        Parameters
        ----------
        model : ModelMapper
            The model which generates instances for different points in parameter space.
        analysis : Analysis
            Contains the data and the log likelihood function which fits an instance of the model to the data, returning
            the log likelihood the `NonLinearSearch` maximizes.

        Returns
        -------
        A result object comprising the Samples object that includes the maximum log likelihood instance and full
        set of accepted ssamples of the fit.
        """

        def prior(cube, ndim, nparams):
            phys_cube = model.vector_from_unit_vector(unit_vector=cube)
            for i in range(len(phys_cube)):
                cube[i] = phys_cube[i]
            return cube

        fitness_function = self.fitness_function_from_model_and_analysis(
            model=model, analysis=analysis
        )
        import pymultinest

        self.logger.info("Beginning MultiNest non-linear search. ")
        pymultinest.run(
            fitness_function,
            prior,
            model.prior_count,
            outputfiles_basename="{}/multinest".format(self.paths.path),
            verbose=(not self.silence),
            **self.config_dict_search
        )
        self.paths.copy_from_sym()

    def samples_from(self, model):
        """
        Create a `Samples` object from this non-linear search's output files on the hard-disk and model.

        For MulitNest, this requires us to load:

            - The parameter samples, log likelihood values and weight_list from the multinest.txt file.
            - The total number of samples (e.g. accepted + rejected) from resume.dat.
            - The log evidence of the model-fit from the multinestsummary.txt file (if this is not yet estimated a
              value of -1.0e99 is used.

        Parameters
        ----------
        model
            The model which generates instances for different points in parameter space. This maps the points from unit
            cube values to physical values via the priors.
        """
        return MultiNestSamples(
            model=model,
            number_live_points=self.config_dict_search["n_live_points"],
            file_summary=path.join(self.paths.samples_path, "multinestsummary.txt"),
            file_weighted_samples=path.join(self.paths.samples_path, "multinest.txt"),
            file_resume=path.join(self.paths.samples_path, "multinestresume.dat"),
            unconverged_sample_size=1,
            time=self.timer.time,
        )
