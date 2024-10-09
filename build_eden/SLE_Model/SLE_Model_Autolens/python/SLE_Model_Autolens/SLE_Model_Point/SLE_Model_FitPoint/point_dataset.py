import SLE_Model_Autogalaxy as ag
from SLE_Model_Autolens.SLE_Model_Point.point_dataset import PointDataset
from SLE_Model_Autolens.SLE_Model_Point.point_solver import PointSolver
from SLE_Model_Autolens.SLE_Model_Point.SLE_Model_FitPoint.fluxes import FitFluxes
from SLE_Model_Autolens.SLE_Model_Point.SLE_Model_FitPoint.positions_image import (
    FitPositionsImage,
)
from SLE_Model_Autolens.SLE_Model_Point.SLE_Model_FitPoint.positions_source import (
    FitPositionsSource,
)
from SLE_Model_Autolens.SLE_Model_Lens.ray_tracing import Tracer
from SLE_Model_Autolens import exc

try:
    import numba

    NumbaException = numba.errors.TypingError
except ModuleNotFoundError:
    NumbaException = AttributeError


class FitPointDataset:
    def __init__(self, point_dataset, tracer, point_solver):
        self.point_dataset = point_dataset
        point_profile = tracer.extract_profile(profile_name=point_dataset.name)
        try:
            if isinstance(point_profile, ag.ps.PointSourceChi):
                self.positions = FitPositionsSource(
                    name=point_dataset.name,
                    positions=point_dataset.positions,
                    noise_map=point_dataset.positions_noise_map,
                    tracer=tracer,
                    point_profile=point_profile,
                )
            else:
                self.positions = FitPositionsImage(
                    name=point_dataset.name,
                    positions=point_dataset.positions,
                    noise_map=point_dataset.positions_noise_map,
                    point_solver=point_solver,
                    tracer=tracer,
                    point_profile=point_profile,
                )
        except exc.PointExtractionException:
            self.positions = None
        except (AttributeError, NumbaException) as e:
            raise exc.FitException from e
        try:
            self.flux = FitFluxes(
                name=point_dataset.name,
                fluxes=point_dataset.fluxes,
                noise_map=point_dataset.fluxes_noise_map,
                positions=point_dataset.positions,
                tracer=tracer,
            )
        except exc.PointExtractionException:
            self.flux = None

    @property
    def log_likelihood(self):
        log_likelihood_positions = (
            self.positions.log_likelihood if (self.positions is not None) else 0.0
        )
        log_likelihood_flux = (
            self.flux.log_likelihood if (self.flux is not None) else 0.0
        )
        return log_likelihood_positions + log_likelihood_flux
