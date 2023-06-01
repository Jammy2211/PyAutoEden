import copy
import itertools
from typing import Type, Union, Tuple
from SLE_Model_Autoconf.class_path import get_class
from SLE_Model_Autofit.SLE_Model_Mapper.identifier import Identifier


class ModelObject:
    _ids = itertools.count()

    @classmethod
    def next_id(cls):
        return next(cls._ids)

    def __init__(self, id_=None, label=None):
        """
        A generic object in AutoFit

        Parameters
        ----------
        id_
            A unique integer identifier. This is used to hash and order priors.
        label
            A label which can optionally be set for visualising this object in a
            graph.
        """
        self.id = id_ or self.next_id()
        self._label = label

    def replacing_for_path(self, path, value):
        """
        Create a new model replacing the value for a given path with a new value

        Parameters
        ----------
        path
            A path indicating the sequence of names used to address an object
        value
            A value that should replace the object at the given path

        Returns
        -------
        A copy of this with an updated value
        """
        new = copy.deepcopy(self)
        obj = new
        for key in path[:(-1)]:
            obj = getattr(obj, key)
        setattr(obj, path[(-1)], value)
        return new

    def has(self, cls):
        """
        Does this instance have an attribute which is of type cls?
        """
        for value in self.__dict__.values():
            if isinstance(value, cls):
                return True
        return False

    @property
    def label(self):
        return self._label

    @label.setter
    def label(self, label):
        self._label = label

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
        from SLE_Model_Autofit.SLE_Model_Mapper.SLE_Model_PriorModel.abstract import (
            AbstractPriorModel,
        )
        from SLE_Model_Autofit.SLE_Model_Mapper.SLE_Model_PriorModel.collection import (
            Collection,
        )
        from SLE_Model_Autofit.SLE_Model_Mapper.SLE_Model_PriorModel.prior_model import (
            Model,
        )
        from SLE_Model_Autofit.SLE_Model_Mapper.SLE_Model_Prior.abstract import Prior
        from SLE_Model_Autofit.SLE_Model_Mapper.SLE_Model_Prior.tuple_prior import (
            TuplePrior,
        )

        if not isinstance(d, dict):
            return d
        type_ = d["type"]
        if type_ == "model":
            instance = Model(get_class(d.pop("class_path")))
        elif type_ == "collection":
            instance = Collection()
        elif type_ == "tuple_prior":
            instance = TuplePrior()
        elif type_ == "dict":
            return {key: ModelObject.from_dict(value) for (key, value) in d.items()}
        elif type_ == "instance":
            d.pop("type")
            cls = get_class(d.pop("class_path"))
            return cls(
                **{key: ModelObject.from_dict(value) for (key, value) in d.items()}
            )
        else:
            try:
                return Prior.from_dict(d)
            except KeyError:
                cls = get_class(type_)
                instance = object.__new__(cls)
        d.pop("type")
        for (key, value) in d.items():
            setattr(instance, key, AbstractPriorModel.from_dict(value))
        return instance

    def dict(self):
        """
        A dictionary representation of this object
        """
        from SLE_Model_Autofit.SLE_Model_Mapper.SLE_Model_PriorModel.abstract import (
            AbstractPriorModel,
        )
        from SLE_Model_Autofit.SLE_Model_Mapper.SLE_Model_PriorModel.collection import (
            Collection,
        )
        from SLE_Model_Autofit.SLE_Model_Mapper.SLE_Model_PriorModel.prior_model import (
            Model,
        )
        from SLE_Model_Autofit.SLE_Model_Mapper.SLE_Model_Prior.tuple_prior import (
            TuplePrior,
        )

        if isinstance(self, Collection):
            type_ = "collection"
        elif isinstance(self, AbstractPriorModel) and (self.prior_count == 0):
            type_ = "instance"
        elif isinstance(self, Model):
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