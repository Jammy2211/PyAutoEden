import numpy as np
from VIS_CTI_Autoarray.VIS_CTI_Structures.VIS_CTI_Arrays.VIS_CTI_OneD.array_1d import (
    Array1D,
)
from VIS_CTI_Autoarray.VIS_CTI_Structures.VIS_CTI_Arrays.VIS_CTI_TwoD.array_2d import (
    Array2D,
)
from VIS_CTI_Autoarray.VIS_CTI_Dataset.interferometer import SettingsInterferometer
from VIS_CTI_Autoarray.VIS_CTI_Inversion.VIS_CTI_Regularization.constant import Constant
from VIS_CTI_Autoarray.VIS_CTI_Inversion.VIS_CTI_Regularization.constant import (
    ConstantSplit,
)
from VIS_CTI_Autoarray.VIS_CTI_Inversion.VIS_CTI_Regularization.adaptive_brightness import (
    AdaptiveBrightness,
)
from VIS_CTI_Autoarray.VIS_CTI_Inversion.VIS_CTI_Regularization.adaptive_brightness import (
    AdaptiveBrightnessSplit,
)
from VIS_CTI_Autoarray.VIS_CTI_Operators.convolver import Convolver
from VIS_CTI_Autoarray.VIS_CTI_Fit.fit_data import FitData
from VIS_CTI_Autoarray.VIS_CTI_Fit.fit_data import FitDataComplex
from VIS_CTI_Autoarray.VIS_CTI_Fit.fit_dataset import FitImaging
from VIS_CTI_Autoarray.VIS_CTI_Fit.fit_dataset import FitInterferometer
from VIS_CTI_Autoarray.VIS_CTI_Structures.VIS_CTI_Grids.VIS_CTI_OneD.grid_1d import (
    Grid1D,
)
from VIS_CTI_Autoarray.VIS_CTI_Structures.VIS_CTI_Grids.VIS_CTI_TwoD.grid_2d import (
    Grid2D,
)
from VIS_CTI_Autoarray.VIS_CTI_Structures.VIS_CTI_Grids.VIS_CTI_TwoD.grid_2d_iterate import (
    Grid2DIterate,
)
from VIS_CTI_Autoarray.VIS_CTI_Structures.VIS_CTI_Grids.VIS_CTI_TwoD.grid_2d_irregular import (
    Grid2DIrregular,
)
from VIS_CTI_Autoarray.VIS_CTI_Structures.VIS_CTI_Grids.VIS_CTI_TwoD.grid_2d_pixelization import (
    Grid2DRectangular,
)
from VIS_CTI_Autoarray.VIS_CTI_Structures.VIS_CTI_Grids.VIS_CTI_TwoD.grid_2d_pixelization import (
    Grid2DDelaunay,
)
from VIS_CTI_Autoarray.VIS_CTI_Structures.VIS_CTI_Grids.VIS_CTI_TwoD.grid_2d_pixelization import (
    Grid2DVoronoi,
)
from VIS_CTI_Autoarray.VIS_CTI_Dataset.imaging import Imaging
from VIS_CTI_Autoarray.VIS_CTI_Dataset.interferometer import Interferometer
from VIS_CTI_Autoarray.VIS_CTI_Structures.kernel_2d import Kernel2D
from VIS_CTI_Autoarray.VIS_CTI_Layout.layout import Layout2D
from VIS_CTI_Autoarray.VIS_CTI_Inversion.VIS_CTI_Mappers.rectangular import (
    MapperRectangularNoInterp,
)
from VIS_CTI_Autoarray.VIS_CTI_Inversion.VIS_CTI_Mappers.delaunay import MapperDelaunay
from VIS_CTI_Autoarray.VIS_CTI_Inversion.VIS_CTI_Mappers.voronoi import (
    MapperVoronoiNoInterp,
)
from VIS_CTI_Autoarray.VIS_CTI_Inversion.VIS_CTI_Mappers.voronoi import MapperVoronoi
from VIS_CTI_Autoarray.VIS_CTI_Mask.mask_1d import Mask1D
from VIS_CTI_Autoarray.VIS_CTI_Mask.mask_2d import Mask2D
from VIS_CTI_Autoarray.VIS_CTI_Operators.transformer import TransformerDFT
from VIS_CTI_Autoarray.VIS_CTI_Operators.transformer import TransformerNUFFT
from VIS_CTI_Autoarray.VIS_CTI_Structures.visibilities import Visibilities
from VIS_CTI_Autoarray.VIS_CTI_Structures.visibilities import VisibilitiesNoiseMap
from VIS_CTI_Autoarray.VIS_CTI_Inversion.VIS_CTI_Inversion.factory import inversion_from


def make_mask_1d_7():
    mask = np.array([True, True, False, False, False, True, True])
    return Mask1D.manual(mask=mask, pixel_scales=(1.0,), sub_size=1)


def make_sub_mask_1d_7():
    mask = np.array([True, True, False, False, False, True, True])
    return Mask1D.manual(mask=mask, pixel_scales=(1.0,), sub_size=2)


def make_mask_2d_7x7():
    mask = np.array(
        [
            [True, True, True, True, True, True, True],
            [True, True, True, True, True, True, True],
            [True, True, False, False, False, True, True],
            [True, True, False, False, False, True, True],
            [True, True, False, False, False, True, True],
            [True, True, True, True, True, True, True],
            [True, True, True, True, True, True, True],
        ]
    )
    return Mask2D.manual(mask=mask, pixel_scales=(1.0, 1.0), sub_size=1)


def make_sub_mask_2d_7x7():
    mask = np.array(
        [
            [True, True, True, True, True, True, True],
            [True, True, True, True, True, True, True],
            [True, True, False, False, False, True, True],
            [True, True, False, False, False, True, True],
            [True, True, False, False, False, True, True],
            [True, True, True, True, True, True, True],
            [True, True, True, True, True, True, True],
        ]
    )
    return Mask2D.manual(mask=mask, sub_size=2, pixel_scales=(1.0, 1.0))


def make_mask_2d_7x7_1_pix():
    mask = np.array(
        [
            [True, True, True, True, True, True, True],
            [True, True, True, True, True, True, True],
            [True, True, True, True, True, True, True],
            [True, True, True, False, True, True, True],
            [True, True, True, True, True, True, True],
            [True, True, True, True, True, True, True],
            [True, True, True, True, True, True, True],
        ]
    )
    return Mask2D.manual(mask=mask, pixel_scales=(1.0, 1.0))


def make_blurring_mask_2d_7x7():
    blurring_mask = np.array(
        [
            [True, True, True, True, True, True, True],
            [True, False, False, False, False, False, True],
            [True, False, True, True, True, False, True],
            [True, False, True, True, True, False, True],
            [True, False, True, True, True, False, True],
            [True, False, False, False, False, False, True],
            [True, True, True, True, True, True, True],
        ]
    )
    return Mask2D.manual(mask=blurring_mask, pixel_scales=(1.0, 1.0))


def make_array_1d_7():
    return Array1D.ones(shape_native=(7,), pixel_scales=(1.0,))


def make_array_2d_7x7():
    return Array2D.ones(shape_native=(7, 7), pixel_scales=(1.0, 1.0))


def make_layout_2d_7x7():
    return Layout2D(
        shape_2d=(7, 7),
        original_roe_corner=(1, 0),
        serial_overscan=(0, 6, 6, 7),
        serial_prescan=(0, 7, 0, 1),
        parallel_overscan=(6, 7, 1, 6),
    )


def make_grid_1d_7():
    return Grid1D.from_mask(mask=make_mask_1d_7())


def make_sub_grid_1d_7():
    return Grid1D.from_mask(mask=make_sub_mask_1d_7())


def make_grid_2d_7x7():
    return Grid2D.from_mask(mask=make_mask_2d_7x7())


def make_sub_grid_2d_7x7():
    return Grid2D.from_mask(mask=make_sub_mask_2d_7x7())


def make_grid_2d_iterate_7x7():
    return Grid2DIterate.from_mask(
        mask=make_mask_2d_7x7(), fractional_accuracy=0.9999, sub_steps=[2, 4, 8, 16]
    )


def make_sub_grid_2d_7x7_simple():
    sub_grid_2d_7x7 = make_sub_grid_2d_7x7()
    sub_grid_2d_7x7[0] = np.array([1.0, 1.0])
    sub_grid_2d_7x7[1] = np.array([1.0, 0.0])
    sub_grid_2d_7x7[2] = np.array([1.0, 1.0])
    sub_grid_2d_7x7[3] = np.array([1.0, 0.0])
    return sub_grid_2d_7x7


def make_blurring_grid_2d_7x7():
    return Grid2D.from_mask(mask=make_blurring_mask_2d_7x7())


def make_convolver_7x7():
    return Convolver(mask=make_mask_2d_7x7(), kernel=make_psf_3x3())


def make_image_7x7():
    return Array2D.ones(shape_native=(7, 7), pixel_scales=(1.0, 1.0))


def make_psf_3x3():
    psf = np.array([[0.0, 0.5, 0.0], [0.5, 1.0, 0.5], [0.0, 0.5, 0.0]])
    return Kernel2D.manual_native(array=psf, pixel_scales=(1.0, 1.0))


def make_psf_3x3_no_blur():
    return Kernel2D.no_blur(pixel_scales=(1.0, 1.0))


def make_noise_map_7x7():
    return Array2D.full(fill_value=2.0, shape_native=(7, 7), pixel_scales=(1.0, 1.0))


def make_grid_2d_irregular_7x7():
    return Grid2DIrregular(grid=[(0.1, 0.1), (0.2, 0.2)])


def make_grid_2d_irregular_7x7_list():
    return [
        Grid2DIrregular(grid=[(0.1, 0.1), (0.2, 0.2)]),
        Grid2DIrregular(grid=[(0.3, 0.3)]),
    ]


def make_imaging_7x7():
    return Imaging(
        image=make_image_7x7(),
        psf=make_psf_3x3(),
        noise_map=make_noise_map_7x7(),
        name="mock_imaging_7x7",
    )


def make_imaging_7x7_no_blur():
    return Imaging(
        image=make_image_7x7(),
        psf=make_psf_3x3_no_blur(),
        noise_map=make_noise_map_7x7(),
        name="mock_imaging_7x7",
    )


def make_visibilities_7():
    return Visibilities.full(shape_slim=(7,), fill_value=1.0)


def make_visibilities_noise_map_7():
    return VisibilitiesNoiseMap.full(shape_slim=(7,), fill_value=2.0)


def make_uv_wavelengths_7x2():
    return np.array(
        [
            [(-55636.4609375), 171376.90625],
            [(-6903.21923828), 51155.578125],
            [(-63488.4140625), 4141.28369141],
            [55502.828125, 47016.7265625],
            [54160.75390625, (-99354.1796875)],
            [(-9327.66308594), (-95212.90625)],
            [0.0, 0.0],
        ]
    )


def make_uv_wavelengths_7x2_no_fft():
    return np.ones(shape=(7, 2))


def make_interferometer_7():
    return Interferometer(
        visibilities=make_visibilities_7(),
        noise_map=make_visibilities_noise_map_7(),
        uv_wavelengths=make_uv_wavelengths_7x2(),
        real_space_mask=make_sub_mask_2d_7x7(),
        settings=SettingsInterferometer(
            grid_class=Grid2D, sub_size=1, transformer_class=TransformerDFT
        ),
    )


def make_interferometer_7_no_fft():
    return Interferometer(
        visibilities=make_visibilities_7(),
        noise_map=make_visibilities_noise_map_7(),
        uv_wavelengths=make_uv_wavelengths_7x2_no_fft(),
        real_space_mask=make_sub_mask_2d_7x7(),
        settings=SettingsInterferometer(
            grid_class=Grid2D, sub_size=1, transformer_class=TransformerDFT
        ),
    )


def make_interferometer_7_grid():
    return Interferometer(
        visibilities=make_visibilities_7(),
        noise_map=make_visibilities_noise_map_7(),
        uv_wavelengths=make_uv_wavelengths_7x2(),
        real_space_mask=make_sub_mask_2d_7x7(),
        settings=SettingsInterferometer(sub_size=1, transformer_class=TransformerDFT),
    )


def make_interferometer_7_lop():
    return Interferometer(
        visibilities=make_visibilities_7(),
        noise_map=make_visibilities_noise_map_7(),
        uv_wavelengths=make_uv_wavelengths_7x2(),
        real_space_mask=make_mask_2d_7x7(),
        settings=SettingsInterferometer(
            sub_size_inversion=1, transformer_class=TransformerNUFFT
        ),
    )


def make_transformer_7x7_7():
    return TransformerDFT(
        uv_wavelengths=make_uv_wavelengths_7x2(), real_space_mask=make_mask_2d_7x7()
    )


def make_masked_imaging_7x7():
    imaging_7x7 = make_imaging_7x7()
    return imaging_7x7.apply_mask(mask=make_sub_mask_2d_7x7())


def make_masked_imaging_7x7_no_blur():
    imaging_7x7 = make_imaging_7x7_no_blur()
    return imaging_7x7.apply_mask(mask=make_sub_mask_2d_7x7())


def make_imaging_fit_x1_plane_7x7():
    imaging_7x7 = make_masked_imaging_7x7()
    fit = FitData(
        data=imaging_7x7.image,
        noise_map=imaging_7x7.noise_map,
        model_data=(5.0 * imaging_7x7.image),
        mask=imaging_7x7.mask,
        use_mask_in_fit=False,
    )
    return FitImaging(dataset=imaging_7x7, fit=fit)


def make_fit_interferometer_7():
    interferometer_7 = make_interferometer_7()
    fit = FitDataComplex(
        data=interferometer_7.visibilities,
        noise_map=interferometer_7.noise_map,
        model_data=(5.0 * interferometer_7.visibilities),
        use_mask_in_fit=False,
    )
    fit_interferometer = FitInterferometer(dataset=interferometer_7, fit=fit)
    return fit_interferometer


def make_regularization_constant():
    return Constant(coefficient=1.0)


def make_regularization_constant_split():
    return ConstantSplit(coefficient=1.0)


def make_regularization_adaptive_brightness():
    return AdaptiveBrightness(
        inner_coefficient=0.1, outer_coefficient=10.0, signal_scale=0.5
    )


def make_regularization_adaptive_brightness_split():
    return AdaptiveBrightnessSplit(
        inner_coefficient=0.1, outer_coefficient=10.0, signal_scale=0.5
    )


def make_rectangular_pixelization_grid_3x3():
    return Grid2DRectangular.overlay_grid(
        grid=make_sub_grid_2d_7x7(), shape_native=(3, 3)
    )


def make_delaunay_pixelization_grid_9():
    grid_9 = Grid2D.manual_slim(
        grid=[
            [0.6, (-0.3)],
            [0.5, (-0.8)],
            [0.2, 0.1],
            [0.0, 0.5],
            [(-0.3), (-0.8)],
            [(-0.6), (-0.5)],
            [(-0.4), (-1.1)],
            [(-1.2), 0.8],
            [(-1.5), 0.9],
        ],
        shape_native=(3, 3),
        pixel_scales=1.0,
    )
    return Grid2DDelaunay(grid=grid_9)


def make_voronoi_pixelization_grid_9():
    grid_9 = Grid2D.manual_slim(
        grid=[
            [0.6, (-0.3)],
            [0.5, (-0.8)],
            [0.2, 0.1],
            [0.0, 0.5],
            [(-0.3), (-0.8)],
            [(-0.6), (-0.5)],
            [(-0.4), (-1.1)],
            [(-1.2), 0.8],
            [(-1.5), 0.9],
        ],
        shape_native=(3, 3),
        pixel_scales=1.0,
    )
    return Grid2DVoronoi(
        grid=grid_9,
        nearest_pixelization_index_for_slim_index=np.zeros(
            shape=make_grid_2d_7x7().shape_slim, dtype="int"
        ),
    )


def make_rectangular_mapper_7x7_3x3():
    return MapperRectangularNoInterp(
        source_grid_slim=make_sub_grid_2d_7x7(),
        source_pixelization_grid=make_rectangular_pixelization_grid_3x3(),
        data_pixelization_grid=None,
        hyper_image=Array2D.ones(shape_native=(3, 3), pixel_scales=0.1),
    )


def make_delaunay_mapper_9_3x3():
    return MapperDelaunay(
        source_grid_slim=make_sub_grid_2d_7x7(),
        source_pixelization_grid=make_delaunay_pixelization_grid_9(),
        data_pixelization_grid=Grid2D.uniform(shape_native=(3, 3), pixel_scales=0.1),
        hyper_image=Array2D.ones(shape_native=(3, 3), pixel_scales=0.1),
    )


def make_voronoi_mapper_9_3x3():
    return MapperVoronoiNoInterp(
        source_grid_slim=make_sub_grid_2d_7x7(),
        source_pixelization_grid=make_voronoi_pixelization_grid_9(),
        data_pixelization_grid=Grid2D.uniform(shape_native=(3, 3), pixel_scales=0.1),
        hyper_image=Array2D.ones(shape_native=(3, 3), pixel_scales=0.1),
    )


def make_voronoi_mapper_nn_9_3x3():
    return MapperVoronoi(
        source_grid_slim=make_sub_grid_2d_7x7(),
        source_pixelization_grid=make_voronoi_pixelization_grid_9(),
        data_pixelization_grid=Grid2D.uniform(shape_native=(3, 3), pixel_scales=0.1),
        hyper_image=Array2D.ones(shape_native=(3, 3), pixel_scales=0.1),
    )


def make_rectangular_inversion_7x7_3x3():
    return inversion_from(
        dataset=make_masked_imaging_7x7(),
        linear_obj_list=[make_rectangular_mapper_7x7_3x3()],
        regularization_list=[make_regularization_constant()],
    )


def make_delaunay_inversion_9_3x3():
    return inversion_from(
        dataset=make_masked_imaging_7x7(),
        linear_obj_list=[make_delaunay_mapper_9_3x3()],
        regularization_list=[make_regularization_constant()],
    )


def make_voronoi_inversion_9_3x3():
    return inversion_from(
        dataset=make_masked_imaging_7x7(),
        linear_obj_list=[make_voronoi_mapper_9_3x3()],
        regularization_list=[make_regularization_constant()],
    )


def make_euclid_data():
    return np.zeros((2086, 2128))


def make_acs_ccd():
    return np.zeros((2068, 4144))


def make_acs_quadrant():
    return np.zeros((2068, 2072))
