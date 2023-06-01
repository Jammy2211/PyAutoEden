import matplotlib.pyplot as plt
from SLE_Model_Autoarray.SLE_Model_Plot.SLE_Model_Wrap.SLE_Model_Base.abstract import (
    AbstractMatWrap,
)


class Annotate(AbstractMatWrap):
    """
    The settings used to customize annotations on the figure.

    This object wraps the following Matplotlib methods:

    - plt.annotate: https://matplotlib.org/3.3.2/api/_as_gen/matplotlib.pyplot.text.html
    """

    def set(self):
        if (
            ("x" not in self.kwargs)
            and ("y" not in self.kwargs)
            and ("s" not in self.kwargs)
        ):
            return
        plt.annotate(**self.config_dict)
