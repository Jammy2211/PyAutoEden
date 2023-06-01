from SLE_Model_Autofit.SLE_Model_Database.SLE_Model_Query.condition import (
    NameCondition,
    ValueCondition,
    StringValueCondition,
    TypeCondition,
)
from SLE_Model_Autofit.SLE_Model_Database.SLE_Model_Query.junction import And, Or
from SLE_Model_Autofit.SLE_Model_Database.SLE_Model_Query.SLE_Model_Query import (
    NamedQuery,
    Attribute,
    BooleanAttribute,
    ChildQuery,
)
from SLE_Model_Autofit.SLE_Model_Database.SLE_Model_Query.SLE_Model_Query.info import *


class N(NameCondition):
    pass


class V(ValueCondition):
    pass


class SV(StringValueCondition):
    pass


class T(TypeCondition):
    pass


class Q(NamedQuery):
    pass


class A(Attribute):
    pass


class BA(BooleanAttribute):
    pass
