from VIS_CTI_Autofit.VIS_CTI_Mapper.VIS_CTI_PriorModel.attribute_pair import (
    AttributeNameValue,
)


class PriorModelNameValue(AttributeNameValue):
    @property
    def prior_model(self):
        return self.value
