import datetime as dt
from SLE_Model_Autoconf import conf
from SLE_Model_Autofit.SLE_Model_Text import formatter as frm, samples_text
from SLE_Model_Autofit.SLE_Model_Tools.util import info_whitespace


def padding(item, target=6):
    string = str(item)
    difference = target - len(string)
    prefix = difference * " "
    return f"{prefix}{string}"


def result_info_from(samples):
    """
    Output the full model.results file, which include the most-likely model, most-probable model at 1 and 3
    sigma confidence and information on the maximum log likelihood.
    """
    results = []
    if hasattr(samples, "log_evidence"):
        if samples.log_evidence is not None:
            results += [
                frm.add_whitespace(
                    str0="Bayesian Evidence ",
                    str1="{:.8f}".format(samples.log_evidence),
                    whitespace=info_whitespace(),
                )
            ]
            results += [
                """
"""
            ]
    results += [
        frm.add_whitespace(
            str0="Maximum Log Likelihood ",
            str1="{:.8f}".format(max(samples.log_likelihood_list)),
            whitespace=info_whitespace(),
        )
    ]
    results += [
        """
"""
    ]
    results += [
        frm.add_whitespace(
            str0="Maximum Log Posterior ",
            str1="{:.8f}".format(max(samples.log_posterior_list)),
            whitespace=info_whitespace(),
        )
    ]
    results += [
        """
"""
    ]
    results += [
        """
""",
        samples.model.parameterization,
        """

""",
    ]
    results += [
        """Maximum Log Likelihood Model:

"""
    ]
    formatter = frm.TextFormatter(line_length=info_whitespace())
    for (i, prior_path) in enumerate(samples.model.unique_prior_paths):
        formatter.add(
            prior_path,
            format_str().format(samples.max_log_likelihood(as_instance=False)[i]),
        )
    results += [
        (
            formatter.text
            + """
"""
        )
    ]
    if hasattr(samples, "pdf_converged"):
        if samples.pdf_converged:
            results += samples_text.summary(
                samples=samples, sigma=3.0, indent=4, line_length=info_whitespace()
            )
            results += [
                """
"""
            ]
            results += samples_text.summary(
                samples=samples, sigma=1.0, indent=4, line_length=info_whitespace()
            )
        else:
            results += [
                """
 WARNING: The samples have not converged enough to compute a PDF and model errors. 
 The model below over estimates errors. 

"""
            ]
            results += samples_text.summary(
                samples=samples, sigma=1.0, indent=4, line_length=info_whitespace()
            )
        results += [
            """

instances
"""
        ]
    formatter = frm.TextFormatter(line_length=info_whitespace())
    for t in samples.model.path_float_tuples:
        formatter.add(*t)
    results += [
        (
            """
"""
            + formatter.text
        )
    ]
    return "".join(results)


def search_summary_from_samples(samples):
    line = [
        f"""Total Samples = {samples.total_samples}
"""
    ]
    if hasattr(samples, "total_accepted_samples"):
        line.append(
            f"""Total Accepted Samples = {samples.total_accepted_samples}
"""
        )
        line.append(
            f"""Acceptance Ratio = {samples.acceptance_ratio}
"""
        )
    if samples.time is not None:
        line.append(
            f"""Time To Run = {dt.timedelta(seconds=float(samples.time))}
"""
        )
        line.append(
            f"""Time Per Sample (seconds) = {(float(samples.time) / samples.total_samples)}
"""
        )
    return line


def search_summary_to_file(samples, log_likelihood_function_time, filename):
    summary = search_summary_from_samples(samples=samples)
    summary.append(
        f"Log Likelihood Function Evaluation Time (seconds) = {log_likelihood_function_time}"
    )
    frm.output_list_of_strings_to_file(file=filename, list_of_strings=summary)


def format_str():
    """The format string for the model.results file, describing to how many decimal points every parameter
    estimate is output in the model.results file.
    """
    decimal_places = conf.instance["general"]["output"]["model_results_decimal_places"]
    return f"{{:.{decimal_places}f}}"
