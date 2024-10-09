from SLE_Model_Autoarray.SLE_Model_Plot.SLE_Model_Wrap.SLE_Model_Base.abstract import (
    set_backend,
)

set_backend()
from SLE_Model_Autoarray.SLE_Model_Plot.SLE_Model_Wrap.SLE_Model_Base.abstract import (
    AbstractMatWrap,
)


class AbstractMatWrap1D(AbstractMatWrap):
    """
    An abstract base class for wrapping matplotlib plotting methods which take as input and plot data structures. For
    example, the `ArrayOverlay` object specifically plots `Array2D` data structures.

    As full description of the matplotlib wrapping can be found in `mat_base.AbstractMatWrap`.
    """

    @property
    def config_folder(self):
        return "mat_wrap_1d"
