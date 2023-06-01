from SLE_Model_Autolens.SLE_Model_Point.point_dataset import PointDict
from SLE_Model_Autolens.SLE_Model_Point.point_solver import PointSolver
from SLE_Model_Autolens.SLE_Model_Lens.ray_tracing import Tracer
from SLE_Model_Autolens.SLE_Model_Point.SLE_Model_FitPoint.point_dataset import (
    FitPointDataset,
)


class FitPointDict(dict):
    def __init__(self, point_dict, tracer, point_solver):
        """
        A fit to a point source dataset, which is stored as a dictionary containing the fit of every data point in a
        entire point-source dataset dictionary.

        This dictionary uses the `name` of the `PointDataset` to act as the key of every entry of the dictionary,
        making it straight forward to access the attributes based on the dataset name.

        Parameters
        ----------
        point_dict
            A dictionary of all point-source datasets that are to be fitted.

        Returns
        -------
        Dict
            A dictionary where the keys are the `name` entries of each dataset in the `PointDict` and the values
            are the corresponding fits to the `PointDataset` it contained.
        """
        self.tracer = tracer
        super().__init__()
        for (key, point_dataset) in point_dict.items():
            self[key] = FitPointDataset(
                point_dataset=point_dataset, tracer=tracer, point_solver=point_solver
            )

    @property
    def log_likelihood(self):
        return sum((fit.log_likelihood for fit in self.values()))
