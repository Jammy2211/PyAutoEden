import copy
from abc import ABC, abstractmethod
from typing import Optional, Set
from VIS_CTI_Autofit.VIS_CTI_Database.VIS_CTI_Query import condition as c
from VIS_CTI_Autofit.VIS_CTI_Database.VIS_CTI_Query.condition import Table


class NotCondition:
    def __init__(self, condition):
        """
        Prepend the condition with a 'not'

        Parameters
        ----------
        condition
            Some condition such equality to a value
        """
        self._condition = condition

    def __str__(self):
        return f"not ({self._condition})"


class AbstractQuery(c.AbstractCondition, ABC):
    def __init__(self, condition=None):
        """
        A query run to find Fit instances that match given
        criteria

        Parameters
        ----------
        condition
            An optional condition
        """
        self._condition = condition

    @property
    def condition(self):
        return self._condition

    @property
    @abstractmethod
    def fit_query(self):
        """
        A full query that can be executed against the database to obtain
        fit ids
        """

    def __str__(self):
        return self.fit_query

    @property
    def tables(self):
        return {c.fit_table}

    def __invert__(self):
        """
        Take ~ of this object.

        The object is copied and its condition is prepended
        with a 'not'.
        """
        inverted = copy.deepcopy(self)
        inverted._condition = NotCondition(self._condition)
        return inverted
