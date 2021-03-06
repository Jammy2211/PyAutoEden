import numpy as np
from typing import List, Tuple
import VIS_CTI_Autoarray as aa
from VIS_CTI_Autocti.VIS_CTI_ChargeInjection.VIS_CTI_Extractor2D.abstract import (
    Extractor2D,
)


class Extractor2DParallelEPER(Extractor2D):
    @property
    def binning_axis(self):
        """
        The axis over which binning is performed to turn a 2D parallel EPER into a 1D EPER.

        For a parallel extractor `axis=1` such that binning is performed over the rows containing the EPER.
        """
        return 1

    def region_list_from(self, pixels):
        """
        Extract the parallel EPERs of every charge injection region on the charge injection image and return as a list
        of 2D arrays.

        The diagram below illustrates the extraction for `pixels=(0, 1)`:

        [] = read-out electronics
        [==========] = read-out register
        [..........] = serial prescan
        [pppppppppp] = parallel overscan
        [ssssssssss] = serial overscan
        [c#cc#c#c#c] = charge injection region (0 / 1 indicate the region index)
        [tttttttttt] = parallel / serial charge injection region trail

               [ppppppppppppppppppppp]
               [ppppppppppppppppppppp]
          [...][t1t1t1t1t1t1t1t1t1t1t][sss]
          [...][c1c1cc1c1cc1cc1ccc1cc][sss]
        | [...][1c1c1cc1c1cc1ccc1cc1c][sss]     |
        | [...][t0t0t0t0t0t0t0t0t0t0t][sss]    | Direction
      Par [...][0t0t0t0t0t0t0t0t0t0t0][sss]    | of
        | [...][0ccc0cccc0cccc0cccc0c][sss]    | clocking
       \\/ [...][cc0ccc0cccc0cccc0cccc][sss]   \\/

        []     [=====================]
               <---------Ser----------

        The extracted regions correspond to the first parallel EPER all charge injection regions:

        region_list[0] = [2, 4, 3, 21] (serial prescan is 3 pixels)
        region_list[1] = [6, 7, 3, 21] (serial prescan is 3 pixels)

        For `pixels=(0,1)` the extracted arrays returned via the `array_2d_list_from()` function keep the first
        parallel EPER of each charge injection region:

        array_2d_list[0] = [t0t0t0tt0t0t0t0t0t0t0]
        array_2d_list[1] = [1t1t1t1t1t1t1t1t1t1t1]

        Parameters
        ----------
        pixels
            The row indexes to extract the trails between (e.g. rows(0, 3) extracts the 1st, 2nd and 3rd rows)
        """
        return [
            region.parallel_trailing_region_from(pixels=pixels)
            for region in self.region_list
        ]
