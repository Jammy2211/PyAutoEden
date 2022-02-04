import itertools
from VIS_CTI_Autoconf.class_path import get_class
from VIS_CTI_Autofit.VIS_CTI_Mapper.identifier import Identifier


class ModelObject:
    _ids = itertools.count()

    def __init__(self, id_=None):
        self.id = next(self._ids) if (id_ is None) else id_

    @property
    def component_number(self):
        return self.id

    def __hash__(self):
        return self.id

    def __eq__(self, other):
        try:
            return self.id == other.id
        except AttributeError:
            return False

    @property
    def identifier(self):
        return str(Identifier(self))

    @staticmethod
    def from_dict(d):
        """
        Recursively parse a dictionary returning the model, collection or
        instance that is represents.

        Parameters
        ----------
        d
            A dictionary representation of some object

        Returns
        -------
        An instance
        """
        from VIS_CTI_Autofit.VIS_CTI_Mapper.VIS_CTI_PriorModel.abstract import (
            AbstractPriorModel,
        )
        from VIS_CTI_Autofit.VIS_CTI_Mapper.VIS_CTI_PriorModel.collection import (
            CollectionPriorModel,
        )
        from VIS_CTI_Autofit.VIS_CTI_Mapper.VIS_CTI_PriorModel.prior_model import (
            PriorModel,
        )
        from VIS_CTI_Autofit.VIS_CTI_Mapper.VIS_CTI_Prior.abstract import Prior
        from VIS_CTI_Autofit.VIS_CTI_Mapper.VIS_CTI_Prior.tuple_prior import TuplePrior

        if not isinstance(d, dict):
            return d
        type_ = d["type"]
        if type_ == "model":
            instance = PriorModel(get_class(d.pop("class_path")))
        elif type_ == "collection":
            instance = CollectionPriorModel()
        elif type_ == "instance":
            cls = get_class(d.pop("class_path"))
            instance = object.__new__(cls)
        elif type_ == "tuple_prior":
            instance = TuplePrior()
        else:
            return Prior.from_dict(d)
        d.pop("type")
        for (key, value) in d.items():
            setattr(instance, key, AbstractPriorModel.from_dict(value))
        return instance

    def dict(self):
        """
        A dictionary representation of this object
        """
        from VIS_CTI_Autofit.VIS_CTI_Mapper.VIS_CTI_PriorModel.abstract import (
            AbstractPriorModel,
        )
        from VIS_CTI_Autofit.VIS_CTI_Mapper.VIS_CTI_PriorModel.collection import (
            CollectionPriorModel,
        )
        from VIS_CTI_Autofit.VIS_CTI_Mapper.VIS_CTI_PriorModel.prior_model import (
            PriorModel,
        )
        from VIS_CTI_Autofit.VIS_CTI_Mapper.VIS_CTI_Prior.tuple_prior import TuplePrior

        if isinstance(self, CollectionPriorModel):
            type_ = "collection"
        elif isinstance(self, AbstractPriorModel) and (self.prior_count == 0):
            type_ = "instance"
        elif isinstance(self, PriorModel):
            type_ = "model"
        elif isinstance(self, TuplePrior):
            type_ = "tuple_prior"
        else:
            raise AssertionError(
                f"{self.__class__.__name__} cannot be serialised to dict"
            )
        dict_ = {"type": type_}
        for (key, value) in self._dict.items():
            try:
                if not isinstance(value, ModelObject):
                    value = AbstractPriorModel.from_instance(value)
                value = value.dict()
            except AttributeError:
                pass
            except TypeError:
                pass
            dict_[key] = value
        return dict_

    @property
    def _dict(self):
        return {
            key: value
            for (key, value) in self.__dict__.items()
            if (
                (key not in ("component_number", "item_number", "id", "cls"))
                and (not key.startswith("_"))
            )
        }
