from typing import Set
from VIS_CTI_Autofit.VIS_CTI_Database.VIS_CTI_Query.condition import (
    AbstractCondition,
    Table,
    info_table,
)
from VIS_CTI_Autofit.VIS_CTI_Database.VIS_CTI_Query.VIS_CTI_Query import AbstractQuery


class InfoQueryCondition(AbstractCondition):
    def __init__(self, key, value):
        """
        Query some item stored in the fit info dictionary

        Parameters
        ----------
        key
        value
        """
        self.key = key
        self.value = value

    @property
    def tables(self):
        return {info_table}

    def __str__(self):
        return f"key = '{self.key}' AND value = '{self.value}'"


class InfoQuery(AbstractQuery):
    def __init__(self, key, value):
        super().__init__(InfoQueryCondition(key=key, value=value))

    @property
    def fit_query(self):
        return f"SELECT fit_id FROM info WHERE {self.condition}"


class InfoField:
    def __init__(self, key):
        self.key = key

    def __eq__(self, other):
        return InfoQuery(self.key, other)


class AnonymousInfo:
    def __getitem__(self, item):
        return InfoField(item)
