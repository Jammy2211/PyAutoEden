from SLE_Model_Autofit.SLE_Model_Mapper.SLE_Model_PriorModel.attribute_pair import (
    AttributeNameValue,
)


class PriorModelNameValue(AttributeNameValue):
    @property
    def prior_model(self):
        return self.value
