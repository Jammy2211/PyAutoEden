import SLE_Model_Autogalaxy as ag
from SLE_Model_Autolens.SLE_Model_Analysis.preloads import Preloads


class FitMaker(ag.FitMaker):
    @property
    def preloads_cls(self):
        return Preloads
