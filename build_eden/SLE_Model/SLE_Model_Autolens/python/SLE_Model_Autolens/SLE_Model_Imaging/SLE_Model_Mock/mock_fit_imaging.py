import SLE_Model_Autoarray as aa
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
        self._grid = grid
        self.tracer = tracer

    @property
    def grid(self):
        if self._grid is not None:
            return self._grid
        return super().grids.uniform

    @property
    def grids(self):
        return aa.GridsInterface(uniform=self.grid, pixelization=self.grid)

    @property
    def tracer_to_inversion(self):
        return MockTracerToInversion(
            tracer=self.tracer,
            image_plane_mesh_grid_pg_list=self.tracer.image_plane_mesh_grid_pg_list,
        )
