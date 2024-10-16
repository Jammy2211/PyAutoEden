from typing import Tuple
from SLE_Model_Autogalaxy.SLE_Model_Profiles import SLE_Model_Mass as mp


class MassLightRelation:
    def __init__(self, gradient=1.0, denominator=1.0, power=0.5):
        self.gradient = gradient
        self.denominator = denominator
        self.power = power

    def einstein_radius_from(self, luminosity):
        return self.gradient * ((luminosity / self.denominator) ** self.power)


class IsothermalSphMLR(mp.IsothermalSph):
    def __init__(self, relation=MassLightRelation(), luminosity=1.0, centre=(0.0, 0.0)):
        self.luminosity = luminosity
        self.relation = relation
        einstein_radius = relation.einstein_radius_from(luminosity=luminosity)
        super().__init__(centre=centre, einstein_radius=einstein_radius)


class IsothermalMLR(mp.Isothermal):
    def __init__(
        self,
        relation=MassLightRelation(),
        luminosity=1.0,
        centre=(0.0, 0.0),
        ell_comps=(0.0, 0.0),
    ):
        self.luminosity = luminosity
        self.relation = relation
        einstein_radius = relation.einstein_radius_from(luminosity=luminosity)
        super().__init__(
            centre=centre, ell_comps=ell_comps, einstein_radius=einstein_radius
        )
