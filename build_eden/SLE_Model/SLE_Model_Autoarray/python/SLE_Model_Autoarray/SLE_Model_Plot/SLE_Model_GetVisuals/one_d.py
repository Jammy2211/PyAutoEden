from SLE_Model_Autoarray.SLE_Model_Plot.SLE_Model_GetVisuals.abstract import (
    AbstractGetVisuals,
)
from SLE_Model_Autoarray.SLE_Model_Plot.SLE_Model_Include.one_d import Include1D
from SLE_Model_Autoarray.SLE_Model_Plot.SLE_Model_Visuals.one_d import Visuals1D
from SLE_Model_Autoarray.SLE_Model_Structures.SLE_Model_Arrays.uniform_1d import Array1D


class GetVisuals1D(AbstractGetVisuals):
    def __init__(self, include, visuals):
        """
        Class which gets 1D attributes and adds them to a `Visuals1D` objects, such that they are plotted on 1D figures.

        For a visual to be extracted and added for plotting, it must have a `True` value in its corresponding entry in
        the `Include1D` object. If this entry is `False`, the `GetVisuals1D.get` method returns a None and the attribute
        is omitted from the plot.

        The `GetVisuals1D` class adds new visuals to a pre-existing `Visuals1D` object that is passed to its `__init__`
        method. This only adds a new entry if the visual are not already in this object.

        Parameters
        ----------
        include
            Sets which 1D visuals are included on the figure that is to be plotted (only entries which are `True`
            are extracted via the `GetVisuals1D` object).
        visuals
            The pre-existing visuals of the plotter which new visuals are added too via the `GetVisuals1D` class.
        """
        super().__init__(include=include, visuals=visuals)

    def via_array_1d_from(self, array_1d):
        """
        From an `Array1D` get its attributes that can be plotted and return them in a `Visuals1D` object.

        Only attributes not already in `self.visuals` and with `True` entries in the `Include1D` object are extracted
        for plotting.

        From an `Array1D` the following attributes can be extracted for plotting:

        - origin: the (y,x) origin of the 1D array's coordinate system.
        - mask: the mask of the 1D array.

        Parameters
        ----------
        array
            The 1D array whose attributes are extracted for plotting.

        Returns
        -------
        Visuals1D
            The collection of attributes that are plotted by a `Plotter` object.
        """
        return self.visuals + self.visuals.__class__(
            origin=self.get("origin", array_1d.origin),
            mask=self.get("mask", array_1d.mask),
        )
