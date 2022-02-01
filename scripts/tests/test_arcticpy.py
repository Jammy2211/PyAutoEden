import os
import sys
from urllib.request import urlretrieve

path = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.join(path, "../.."))
import numpy as np
import pytest
import matplotlib.pyplot as plt

from SHE_ArCTICPy import cti
from SHE_ArCTICPy.ccd import CCDPhase, CCD
from SHE_ArCTICPy.roe import ROE
from SHE_ArCTICPy.traps import TrapInstantCapture


class TestCompareOldArCTIC:
    def test__add_cti__single_pixel__vary_express__compare_old_arctic(self):

        # Manually set True to make the plot
        do_plot = False
        # do_plot = True

        image_pre_cti = np.zeros((20, 1))
        image_pre_cti[2, 0] = 800

        # Nice numbers for easy manual checking
        traps = [TrapInstantCapture(density=10, release_timescale=-1 / np.log(0.5))]
        ccd = CCD(
            phases=[
                CCDPhase(well_fill_power=1, full_well_depth=1000, well_notch_depth=0)
            ]
        )
        roe = ROE(
            empty_traps_between_columns=True,
            empty_traps_for_first_transfers=False,
            use_integer_express_matrix=True,
        )

        for i, (express, image_idl) in enumerate(
            zip(
                [1, 2, 5, 10, 20],
                [
                    [
                        0.00000,
                        0.00000,
                        776.000,
                        15.3718,
                        9.65316,
                        5.81950,
                        3.41087,
                        1.95889,
                        1.10817,
                        0.619169,
                        0.342489,
                        0.187879,
                        0.102351,
                        0.0554257,
                        0.0298603,
                        0.0160170,
                        0.00855758,
                        0.00455620,
                        0.00241824,
                        0.00128579,
                    ],
                    [
                        0.00000,
                        0.00000,
                        776.000,
                        15.3718,
                        9.65316,
                        5.81950,
                        3.41087,
                        1.95889,
                        1.10817,
                        0.619169,
                        0.348832,
                        0.196128,
                        0.109984,
                        0.0614910,
                        0.0340331,
                        0.0187090,
                        0.0102421,
                        0.00558406,
                        0.00303254,
                        0.00164384,
                    ],
                    [
                        0.00000,
                        0.00000,
                        776.000,
                        15.3718,
                        9.59381,
                        5.80216,
                        3.43231,
                        1.99611,
                        1.15104,
                        0.658983,
                        0.374685,
                        0.211807,
                        0.119441,
                        0.0670274,
                        0.0373170,
                        0.0205845,
                        0.0113179,
                        0.00621127,
                        0.00341018,
                        0.00187955,
                    ],
                    [
                        0.00000,
                        0.00000,
                        776.160,
                        15.1432,
                        9.51562,
                        5.78087,
                        3.43630,
                        2.01144,
                        1.16452,
                        0.668743,
                        0.381432,
                        0.216600,
                        0.122556,
                        0.0689036,
                        0.0383241,
                        0.0211914,
                        0.0116758,
                        0.00641045,
                        0.00352960,
                        0.00195050,
                    ],
                    [
                        0.00000,
                        0.00000,
                        776.239,
                        15.0315,
                        9.47714,
                        5.77145,
                        3.43952,
                        2.01754,
                        1.17049,
                        0.673351,
                        0.384773,
                        0.218860,
                        0.124046,
                        0.0697859,
                        0.0388253,
                        0.0214799,
                        0.0118373,
                        0.00650488,
                        0.00358827,
                        0.00198517,
                    ],
                ],
            )
        ):
            image_post_cti = cti.add_cti(
                image=image_pre_cti,
                parallel_roe=roe,
                parallel_ccd=ccd,
                parallel_traps=traps,
                parallel_express=express,
                verbosity=0,
            ).T[0]

            image_idl = np.array(image_idl)

            assert image_post_cti == pytest.approx(image_idl, rel=0.05)
