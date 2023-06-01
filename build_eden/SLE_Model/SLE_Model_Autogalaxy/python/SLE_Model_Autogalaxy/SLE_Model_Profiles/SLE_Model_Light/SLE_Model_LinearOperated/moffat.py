from SLE_Model_Autogalaxy.SLE_Model_Profiles.SLE_Model_Light import (
    SLE_Model_Operated as lp_operated,
)
from SLE_Model_Autogalaxy.SLE_Model_Profiles.SLE_Model_Light import (
    SLE_Model_Linear as lp_linear,
)


class Moffat(lp_linear.Moffat, lp_operated.LightProfileOperated):
    pass
