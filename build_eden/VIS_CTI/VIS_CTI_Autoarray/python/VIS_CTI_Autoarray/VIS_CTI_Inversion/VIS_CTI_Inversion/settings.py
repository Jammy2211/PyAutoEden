import logging

logging.basicConfig()
logger = logging.getLogger(__name__)


class SettingsInversion:
    def __init__(
        self,
        use_w_tilde=True,
        use_linear_operators=False,
        tolerance=1e-08,
        maxiter=250,
        check_solution=True,
        use_curvature_matrix_preload=True,
    ):
        self.use_w_tilde = use_w_tilde
        self.use_linear_operators = use_linear_operators
        self.tolerance = tolerance
        self.maxiter = maxiter
        self.check_solution = check_solution
        self.use_curvature_matrix_preload = use_curvature_matrix_preload
