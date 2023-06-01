import SLE_Model_Autoarray as aa
from SLE_Model_Autolens.SLE_Model_Lens.to_inversion import TracerToInversion
from SLE_Model_Autolens.SLE_Model_Lens.SLE_Model_Mock.mock_to_inversion import (
    MockTracerToInversion,
)


class MockFitImaging(aa.m.MockFitImaging):
    def __init__(
        self,
        tracer=None,
        dataset=aa.m.MockDataset(),
        inversion=None,
        noise_map=None,
        grid=None,
        blurred_image=None,
    ):
        super().__init__(
            dataset=dataset,
            inversion=inversion,
            noise_map=noise_map,
            blurred_image=blurred_image,
        )
        self.tracer = tracer
        self.grid = grid

    @property
    def tracer_to_inversion(self):
        return MockTracerToInversion(
            tracer=self.tracer,
            sparse_image_plane_grid_pg_list=self.tracer.sparse_image_plane_grid_pg_list,
        )
