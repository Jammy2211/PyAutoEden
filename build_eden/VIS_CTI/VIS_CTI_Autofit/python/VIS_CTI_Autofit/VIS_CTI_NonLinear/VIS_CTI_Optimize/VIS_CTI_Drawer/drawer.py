from os import path
from typing import Optional
from VIS_CTI_Autofit.VIS_CTI_Database.sqlalchemy_ import sa
from VIS_CTI_Autoconf import conf
from VIS_CTI_Autofit.VIS_CTI_Mapper.VIS_CTI_PriorModel.abstract import (
    AbstractPriorModel,
)
from VIS_CTI_Autofit.VIS_CTI_NonLinear.VIS_CTI_Optimize.abstract_optimize import (
    AbstractOptimizer,
)
from VIS_CTI_Autofit.VIS_CTI_NonLinear.abstract_search import PriorPasser
from VIS_CTI_Autofit.VIS_CTI_NonLinear.initializer import Initializer
from VIS_CTI_Autofit.VIS_CTI_NonLinear.VIS_CTI_Optimize.VIS_CTI_Drawer.plotter import (
    DrawerPlotter,
)
from VIS_CTI_Autofit.VIS_CTI_NonLinear.VIS_CTI_Samples import Samples, Sample
from VIS_CTI_Autofit.VIS_CTI_Plot.output import Output


class Drawer(AbstractOptimizer):
    __identifier_fields__ = ("total_draws",)

    def __init__(
        self,
        name=None,
        path_prefix=None,
        unique_tag=None,
        prior_passer=None,
        initializer=None,
        iterations_per_update=None,
        session=None,
        **kwargs,
    ):
        """
        A Drawer non-linear search, which simply draws a fixed number of samples from the model uniformly from the
        priors.

        Therefore, it does not seek to determine model parameters which maximize the likelihood or map out the
        posterior of the overall parameter space.

        Whilst this is not the typical use case of a non-linear search, it has certain niche applications, for example:

        - Given a model one can determine how much variation there is in the log likelihood / log posterior values.
        By visualizing this as a histogram one can therefore quantify the behaviour of that
        model's `log_likelihood_function`.

        - If the `log_likelihood_function` of a model is stochastic (e.g. different values of likelihood may be
        computed for an identical model due to randomness in the likelihood evaluation) this search can quantify
        the behaviour of that stochasticity.

        - For advanced modeling tools, for example sensitivity mapping performed via the `Sensitivity` object,
        the `Drawer` search may be sufficient to perform the overall modeling task, without the need of performing
        an actual parameter space search.

        The drawer search itself is performed by simply reusing the functionality of the `Initializer` object.
        Whereas this is normally used to initialize a non-linear search, for the drawer it performed all log
        likelihood evluations.

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
        initializer
            Generates the initialize samples of non-linear parameter space (see autofit.non_linear.initializer).
        session
            An SQLalchemy session instance so the results of the model-fit are written to an SQLite database.
        """
        super().__init__(
            name=name,
            path_prefix=path_prefix,
            unique_tag=unique_tag,
            prior_passer=prior_passer,
            initializer=initializer,
            iterations_per_update=iterations_per_update,
            session=session,
            **kwargs,
        )
        self.number_of_cores = 1
        self.logger.debug("Creating Drawer Search")

    class Fitness(AbstractOptimizer.Fitness):
        def figure_of_merit_from(self, parameter_list):
            """
            The figure of merit is the value that the `NonLinearSearch` uses to sample parameter space.

            The `Drawer` search can use either the log posterior values or log likelihood values.
            """
            return self.log_posterior_from(parameter_list=parameter_list)

    def _fit(self, model, analysis, log_likelihood_cap=None):
        """
        Fit a model using Drawer and the Analysis class which contains the data and returns the log likelihood from
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
        A result object comprising the Samples object that inclues the maximum log likelihood instance and full
        chains used by the fit.
        """
        fitness_function = self.fitness_function_from_model_and_analysis(
            model=model, analysis=analysis
        )
        total_draws = self.config_dict_search["total_draws"]
        self.logger.info(
            f"Performing DrawerSearch for a total of {total_draws} points."
        )
        (
            unit_parameter_lists,
            parameter_lists,
            log_posterior_list,
        ) = self.initializer.samples_from_model(
            total_points=self.config_dict_search["total_draws"],
            model=model,
            fitness_function=fitness_function,
            use_prior_medians=True,
        )
        self.paths.save_object("parameter_lists", parameter_lists)
        self.paths.save_object("log_posterior_list", log_posterior_list)
        self.perform_update(model=model, analysis=analysis, during_analysis=False)
        self.logger.info("Drawer complete")

    def fitness_function_from_model_and_analysis(
        self, model, analysis, log_likelihood_cap=None
    ):
        return Drawer.Fitness(
            paths=self.paths,
            model=model,
            analysis=analysis,
            samples_from_model=self.samples_from,
            log_likelihood_cap=log_likelihood_cap,
        )

    def samples_from(self, model):
        parameter_lists = self.paths.load_object("parameter_lists")
        log_prior_list = [
            sum(model.log_prior_list_from_vector(vector=vector))
            for vector in parameter_lists
        ]
        log_likelihood_list = [
            (lp - prior)
            for (lp, prior) in zip(
                self.paths.load_object("log_posterior_list"), log_prior_list
            )
        ]
        weight_list = len(log_likelihood_list) * [1.0]
        sample_list = Sample.from_lists(
            model=model,
            parameter_lists=parameter_lists,
            log_likelihood_list=log_likelihood_list,
            log_prior_list=log_prior_list,
            weight_list=weight_list,
        )
        return Samples(model=model, sample_list=sample_list, time=self.timer.time)

    def plot_results(self, samples):
        def should_plot(name):
            return conf.instance["visualize"]["plots_search"]["drawer"][name]

        plotter = DrawerPlotter(
            samples=samples,
            output=Output(
                path=path.join(self.paths.image_path, "search"), format="png"
            ),
        )
