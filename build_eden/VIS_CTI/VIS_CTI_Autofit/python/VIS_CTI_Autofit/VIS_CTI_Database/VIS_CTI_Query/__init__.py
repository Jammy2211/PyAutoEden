from VIS_CTI_Autofit.VIS_CTI_Database.VIS_CTI_Query.condition import (
    NameCondition,
    ValueCondition,
    StringValueCondition,
    TypeCondition,
)
from VIS_CTI_Autofit.VIS_CTI_Database.VIS_CTI_Query.junction import And, Or
from VIS_CTI_Autofit.VIS_CTI_Database.VIS_CTI_Query.VIS_CTI_Query import (
    NamedQuery,
    Attribute,
    BooleanAttribute,
    ChildQuery,
)
from VIS_CTI_Autofit.VIS_CTI_Database.VIS_CTI_Query.VIS_CTI_Query.info import *


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
