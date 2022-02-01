from VIS_CTI_Autofit.VIS_CTI_Mapper.model import ModelInstance
from VIS_CTI_Autofit.VIS_CTI_Mapper.VIS_CTI_PriorModel.prior_model import PriorModel
from VIS_CTI_Autofit.VIS_CTI_Mapper.model_mapper import ModelMapper

from VIS_CTI_Autofit.VIS_CTI_Mock import mock_model


class TestCase:
    def test_transfer_tuples(self):

        model = ModelMapper()
        instance = ModelInstance()

        model.profile = PriorModel(mock_model.MockClassx2Tuple)
        assert model.prior_count == 2

        result = model.copy_with_fixed_priors(instance)
        assert result.prior_count == 2

        instance.profile = mock_model.MockClassx2Tuple()

        result = model.copy_with_fixed_priors(instance)
        assert result.prior_count == 0
        assert result.profile.one_tuple == (0.0, 0.0)
        assert isinstance(result.profile, PriorModel)

        instance = result.instance_from_unit_vector([])
        assert result.profile.one_tuple == (0.0, 0.0)
        assert isinstance(instance.profile, mock_model.MockClassx2Tuple)
