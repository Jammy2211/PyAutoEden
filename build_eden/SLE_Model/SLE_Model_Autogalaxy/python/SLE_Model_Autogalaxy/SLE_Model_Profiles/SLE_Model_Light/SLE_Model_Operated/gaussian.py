from SLE_Model_Autogalaxy.SLE_Model_Profiles.SLE_Model_Light import (
    SLE_Model_Standard as lp,
)
from SLE_Model_Autogalaxy.SLE_Model_Profiles.SLE_Model_Light.SLE_Model_Operated.abstract import (
    LightProfileOperated,
)


class Gaussian(lp.Gaussian, LightProfileOperated):
    pass
