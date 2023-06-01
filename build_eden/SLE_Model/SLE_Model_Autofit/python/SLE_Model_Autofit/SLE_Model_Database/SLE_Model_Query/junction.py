from abc import ABC, abstractmethod
from collections import defaultdict
from typing import Set, Iterable
from SLE_Model_Autofit.SLE_Model_Database.SLE_Model_Query.condition import (
    AbstractCondition,
    Table,
    none_table,
)


class AbstractJunction(AbstractCondition, ABC):
    def __new__(cls, *conditions: AbstractCondition):
        """
        If only a single extant condition is passed in then that
        condition should simply be returned.
        """
        conditions = cls._match_conditions(conditions)
        if len(conditions) == 1:
            return list(conditions)[0]
        return object.__new__(cls)

    def __init__(self, *conditions: AbstractCondition):
        """
        A combination of two or more conditions. A set of rules allow
        the query to be expressed in the simplest terms possible

        Any subjunctions of the same type are unwrapped.
        i.e. And(A, B) & And(C, D) -> And(A, B, C, D)

        Conditions are a set so duplication is removed.
        i.e. And(A, B, A) -> And(A, B)

        NamedQuery child conditions are matched by their name creating
        one NameQuery for each name and applying the junction type to
        their conditions.
        i.e. And(Named('name', A), Named('name', B)) -> Named('name', And(A, B))

        An AttributeQuery is on an attribute of the fit class. If an AttributeQuery
        is present in a conjunction then the fit_query must be returned instead
        of a string.

        Parameters
        ----------
        conditions
            A list of SQL conditions
        """
        from SLE_Model_Autofit.SLE_Model_Database.SLE_Model_Query.SLE_Model_Query.attribute import (
            AttributeQuery,
        )

        self.conditions = self._match_conditions(conditions)
        self.is_fit_only = any(
            map(
                (lambda condition: isinstance(condition, AttributeQuery)),
                self.conditions,
            )
        )

    @property
    def fit_query(self):
        subqueries = [f"id IN ({condition.fit_query})" for condition in self.conditions]
        condition_string = f" {self.join} ".join(subqueries)
        return f"SELECT id FROM fit WHERE {condition_string}"

    @classmethod
    def _match_conditions(cls, conditions):
        """
        Simplifies the query by matching named queries and combining junctions.

        See __init__
        """
        from SLE_Model_Autofit.SLE_Model_Database.SLE_Model_Query.SLE_Model_Query import (
            NamedQuery,
        )

        new_conditions = set()
        named_query_dict = defaultdict(set)

        def add_conditions(conditions_):
            for condition in conditions_:
                if condition is None:
                    continue
                if isinstance(condition, cls):
                    add_conditions(condition)
                elif isinstance(condition, NamedQuery) and (
                    none_table not in condition.tables
                ):
                    named_query_dict[condition.name].add(condition)
                else:
                    new_conditions.add(condition)

        add_conditions(conditions)
        for (name, queries) in named_query_dict.items():
            new_conditions.add(
                NamedQuery(name, cls(*[query.other_condition for query in queries]))
            )
        return new_conditions

    def __iter__(self):
        return iter(sorted(self.conditions))

    @property
    def tables(self):
        """
        Combines the tables of all subqueries which are not
        named queries
        """
        from SLE_Model_Autofit.SLE_Model_Database.SLE_Model_Query.SLE_Model_Query import (
            NamedQuery,
        )

        return {
            table
            for condition in self.conditions
            if (not isinstance(condition, NamedQuery))
            for table in condition.tables
        }

    @property
    @abstractmethod
    def join(self):
        """
        SQL string used to conjoin queries
        """

    def __str__(self):
        """
        SQL string expressing combined query
        """
        if self.is_fit_only:
            return self.fit_query
        string = f" {self.join} ".join(map(str, sorted(self.conditions)))
        return f"({string})"


class And(AbstractJunction):
    @property
    def join(self):
        return "AND"


class Or(AbstractJunction):
    @property
    def join(self):
        return "OR"
