from VIS_CTI_Autofit.VIS_CTI_Database.VIS_CTI_Query import condition as c
from VIS_CTI_Autofit.VIS_CTI_Database.VIS_CTI_Query.VIS_CTI_Query.abstract import (
    AbstractQuery,
)


class AttributeQuery(AbstractQuery):
    @property
    def fit_query(self):
        """
        The SQL string produced by this query. This is applied directly to the database.
        """
        return f"SELECT id FROM fit WHERE {self.condition}"


class Attribute:
    def __init__(self, attribute):
        """
        Some direct attribute of the Fit class

        Parameters
        ----------
        attribute
            The name of that attribute
        """
        self.attribute = attribute

    def _make_query(self, cls, value):
        """
        Create a query against this attribute

        Parameters
        ----------
        cls
            An AttributeCondition that describes the query
        value
            The value that the attribute is compared to

        Returns
        -------
        A query on ids of the fit table
        """
        return AttributeQuery(cls(attribute=self.attribute, value=value))

    def __eq__(self, other):
        """
        Check whether an attribute, such as a search name, is equal
        to some value
        """
        return self._make_query(cls=c.EqualityAttributeCondition, value=other)

    def in_(self, item):
        """
        Check whether an attribute is contained within a substring
        """
        return self._make_query(cls=c.InAttributeCondition, value=item)

    def contains(self, item):
        """
        Check whether an attribute, such as a search name, contains
        some string
        """
        return self._make_query(cls=c.ContainsAttributeCondition, value=item)


class BooleanAttribute(Attribute, AttributeQuery):
    def __init__(self, attribute):
        super().__init__(attribute)
        super(AttributeQuery, self).__init__(c.AttributeCondition(attribute))

    def __hash__(self):
        return hash(str(self))


class ChildQuery(AttributeQuery):
    def __init__(self, predicate):
        super().__init__(predicate)

    @property
    def condition(self):
        return f"parent_id in ({super().condition})"


class BestFitQuery(ChildQuery):
    def __init__(self, predicate):
        super().__init__(predicate)

    @property
    def fit_query(self):
        return f"""WITH children AS (
                    SELECT id, parent_id, max_log_likelihood 
                    FROM fit WHERE {self.condition}
                   ), 
                   best AS (
                    SELECT parent_id, max(max_log_likelihood) AS max_log_likelihood 
                    FROM children 
                    GROUP BY parent_id
                   ) 
                   SELECT id 
                   FROM children, best 
                   WHERE children.parent_id = best.parent_id 
                   AND children.max_log_likelihood = best.max_log_likelihood;
               """
