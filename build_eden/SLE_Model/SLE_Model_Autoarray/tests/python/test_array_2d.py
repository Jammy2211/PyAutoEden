import os
from os import path

import numpy as np
import pytest

import SLE_Model_Autoarray as aa

test_data_dir = path.join(
    "{}".format(os.path.dirname(os.path.realpath(__file__))), "files"
)


class TestAPI:
    def test__manual(self):

        arr = aa.Array2D.no_mask(
            values=[[1.0, 2.0], [3.0, 4.0]],
            pixel_scales=1.0,
        )

        assert type(arr) == aa.Array2D
        assert (arr == np.array([1.0, 2.0, 3.0, 4.0])).all()
        assert (arr.native == np.array([[1.0, 2.0], [3.0, 4.0]])).all()
        assert (arr.slim == np.array([1.0, 2.0, 3.0, 4.0])).all()
        assert arr.pixel_scales == (1.0, 1.0)
        assert arr.origin == (0.0, 0.0)

    def test__manual_mask(self):

        mask = aa.Mask2D.all_false(shape_native=(2, 2), pixel_scales=1.0)
        arr = aa.Array2D(values=[[1.0, 2.0], [3.0, 4.0]], mask=mask)

        assert type(arr) == aa.Array2D
        assert (arr.native == np.array([[1.0, 2.0], [3.0, 4.0]])).all()
        assert (arr.slim == np.array([1.0, 2.0, 3.0, 4.0])).all()
        assert arr.pixel_scales == (1.0, 1.0)
        assert arr.origin == (0.0, 0.0)

        mask = aa.Mask2D(
            mask=[[False, False], [True, False]], pixel_scales=1.0, origin=(0.0, 1.0)
        )
        arr = aa.Array2D(values=[1.0, 2.0, 4.0], mask=mask)

        assert type(arr) == aa.Array2D
        assert (arr.native == np.array([[1.0, 2.0], [0.0, 4.0]])).all()
        assert (arr.slim == np.array([1.0, 2.0, 4.0])).all()
        assert arr.pixel_scales == (1.0, 1.0)
        assert arr.origin == (0.0, 1.0)

        mask = aa.Mask2D(
            mask=[[False, False], [True, False]], pixel_scales=1.0, origin=(0.0, 1.0)
        )
        arr = aa.Array2D(values=[[1.0, 2.0], [3.0, 4.0]], mask=mask)

        assert type(arr) == aa.Array2D
        assert (arr.native == np.array([[1.0, 2.0], [0.0, 4.0]])).all()
        assert (arr.slim == np.array([1.0, 2.0, 4.0])).all()
        assert arr.pixel_scales == (1.0, 1.0)
        assert arr.origin == (0.0, 1.0)

    def test__full__makes_scaled_array_with_pixel_scale(self):

        arr = aa.Array2D.ones(shape_native=(2, 2), pixel_scales=1.0)

        assert type(arr) == aa.Array2D
        assert (arr.native == np.array([[1.0, 1.0], [1.0, 1.0]])).all()
        assert (arr.slim == np.array([1.0, 1.0, 1.0, 1.0])).all()
        assert arr.pixel_scales == (1.0, 1.0)
        assert arr.origin == (0.0, 0.0)

        arr = aa.Array2D.full(
            fill_value=2.0, shape_native=(2, 2), pixel_scales=1.0, origin=(0.0, 1.0)
        )

        assert type(arr) == aa.Array2D
        assert (arr.native == np.array([[2.0, 2.0], [2.0, 2.0]])).all()
        assert (arr.slim == np.array([2.0, 2.0, 2.0, 2.0])).all()
        assert arr.pixel_scales == (1.0, 1.0)
        assert arr.origin == (0.0, 1.0)

    def test__ones_zeros__makes_array_without_other_inputs(self):

        arr = aa.Array2D.ones(shape_native=(2, 2), pixel_scales=1.0)

        assert type(arr) == aa.Array2D
        assert (arr.native == np.array([[1.0, 1.0], [1.0, 1.0]])).all()
        assert (arr.slim == np.array([1.0, 1.0, 1.0, 1.0])).all()

        arr = aa.Array2D.zeros(shape_native=(2, 2), pixel_scales=1.0)

        assert type(arr) == aa.Array2D
        assert (arr == np.array([0.0, 0.0, 0.0, 0.0])).all()
        assert (arr.native == np.array([[0.0, 0.0], [0.0, 0.0]])).all()
        assert (arr.slim == np.array([0.0, 0.0, 0.0, 0.0])).all()

    def test__ones_zeros__makes_scaled_array_with_pixel_scale(self):

        arr = aa.Array2D.ones(shape_native=(2, 2), pixel_scales=1.0)

        assert type(arr) == aa.Array2D
        assert (arr.native == np.array([[1.0, 1.0], [1.0, 1.0]])).all()
        assert (arr.slim == np.array([1.0, 1.0, 1.0, 1.0])).all()
        assert arr.pixel_scales == (1.0, 1.0)
        assert arr.origin == (0.0, 0.0)

        arr = aa.Array2D.zeros(shape_native=(2, 2), pixel_scales=1.0, origin=(0.0, 1.0))

        assert type(arr) == aa.Array2D
        assert (arr.native == np.array([[0.0, 0.0], [0.0, 0.0]])).all()
        assert (arr.slim == np.array([0.0, 0.0, 0.0, 0.0])).all()
        assert arr.pixel_scales == (1.0, 1.0)
        assert arr.origin == (0.0, 1.0)

    def test__ones_zeros__makes_scaled_sub_array_with_pixel_scale(self):

        arr = aa.Array2D.ones(shape_native=(1, 4), pixel_scales=1.0)

        assert type(arr) == aa.Array2D
        assert (arr.native == np.array([[1.0, 1.0, 1.0, 1.0]])).all()
        assert (arr.slim == np.array([1.0, 1.0, 1.0, 1.0])).all()
        assert arr.pixel_scales == (1.0, 1.0)
        assert arr.origin == (0.0, 0.0)

    def test__from_fits__makes_array_without_other_inputs(self):

        arr = aa.Array2D.from_fits(
            file_path=path.join(test_data_dir, "3x3_ones.fits"), hdu=0, pixel_scales=1.0
        )

        assert type(arr) == aa.Array2D
        assert (arr.native == np.ones((3, 3))).all()
        assert (arr.slim == np.ones(9)).all()

        arr = aa.Array2D.from_fits(
            file_path=path.join(test_data_dir, "4x3_ones.fits"), hdu=0, pixel_scales=1.0
        )

        assert type(arr) == aa.Array2D
        assert (arr == np.ones((12,))).all()
        assert (arr.native == np.ones((4, 3))).all()
        assert (arr.slim == np.ones((12,))).all()

    def test__from_fits__loads_and_stores_header_info(self):

        arr = aa.Array2D.from_fits(
            file_path=path.join(test_data_dir, "3x3_ones.fits"), hdu=0, pixel_scales=1.0
        )

        assert arr.header.header_sci_obj["BITPIX"] == -64
        assert arr.header.header_hdu_obj["BITPIX"] == -64

        arr = aa.Array2D.from_fits(
            file_path=path.join(test_data_dir, "4x3_ones.fits"), hdu=0, pixel_scales=1.0
        )

        assert arr.header.header_sci_obj["BITPIX"] == -64
        assert arr.header.header_hdu_obj["BITPIX"] == -64

    def test__from_yx_values__use_input_values_which_swap_values_from_top_left_notation(
        self,
    ):

        arr = aa.Array2D.from_yx_and_values(
            y=[0.5, 0.5, -0.5, -0.5],
            x=[-0.5, 0.5, -0.5, 0.5],
            values=[1.0, 2.0, 3.0, 4.0],
            shape_native=(2, 2),
            pixel_scales=1.0,
        )

        assert (arr.native == np.array([[1.0, 2.0], [3.0, 4.0]])).all()

        arr = aa.Array2D.from_yx_and_values(
            y=[-0.5, 0.5, 0.5, -0.5],
            x=[-0.5, 0.5, -0.5, 0.5],
            values=[1.0, 2.0, 3.0, 4.0],
            shape_native=(2, 2),
            pixel_scales=1.0,
        )

        assert (arr.native == np.array([[3.0, 2.0], [1.0, 4.0]])).all()

        arr = aa.Array2D.from_yx_and_values(
            y=[-0.5, 0.5, 0.5, -0.5],
            x=[0.5, 0.5, -0.5, -0.5],
            values=[1.0, 2.0, 3.0, 4.0],
            shape_native=(2, 2),
            pixel_scales=1.0,
        )

        assert (arr.native == np.array([[4.0, 2.0], [1.0, 3.0]])).all()

        arr = aa.Array2D.from_yx_and_values(
            y=[1.0, 1.0, 0.0, 0.0, -1.0, -1.0],
            x=[-0.5, 0.5, -0.5, 0.5, -0.5, 0.5],
            values=[1.0, 2.0, 3.0, 4.0, 5.0, 6.0],
            shape_native=(3, 2),
            pixel_scales=1.0,
        )

        assert (arr.native == np.array([[1.0, 2.0], [3.0, 4.0], [5.0, 6.0]])).all()

        arr = aa.Array2D.from_yx_and_values(
            y=[0.0, 1.0, -1.0, 0.0, -1.0, 1.0],
            x=[-0.5, 0.5, 0.5, 0.5, -0.5, -0.5],
            values=[1.0, 2.0, 3.0, 4.0, 5.0, 6.0],
            shape_native=(3, 2),
            pixel_scales=1.0,
        )

        assert (arr.native == np.array([[3.0, 2.0], [6.0, 4.0], [5.0, 1.0]])).all()
