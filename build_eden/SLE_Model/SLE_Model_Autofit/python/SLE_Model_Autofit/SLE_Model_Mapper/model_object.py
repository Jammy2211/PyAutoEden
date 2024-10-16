import copy
import itertools
from typing import Type, Union, Tuple, Optional, Dict
import logging
from SLE_Model_Autoconf.class_path import get_class
from SLE_Model_Autoconf.dictable import from_dict, to_dict
from SLE_Model_Autofit.SLE_Model_Mapper.identifier import Identifier

logger = logging.getLogger(__name__)


def dereference(reference, name):
    if reference is None:
        return None
    updated = {}
    for (key, value) in reference.items():
        array = key.split(".")
        if array[0] == name:
            updated[".".join(array[1:])] = value
    return updated


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
        self.id = int((self.next_id() if (id_ is None) else id_))
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
            if isinstance(key, int):
                obj = obj[key]
            else:
                obj = getattr(obj, key)
        key = path[(-1)]
        if isinstance(key, int):
            obj[key] = value
        else:
            setattr(obj, key, value)
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

    @classmethod
    def from_dict(cls, d, reference=None, loaded_ids=None):
        """
        Recursively parse a dictionary returning the model, collection or
        instance that is represents.

        Parameters
        ----------
        d
            A dictionary representation of some object
        reference
            An optional dictionary mapping names to class paths. This is used
            to specify the type of a model or instance.

            Maps paths to class paths. For example:
            "path.in.model": "path.to.Class"

            In this case, the class path "path.to.Class" will be used to
            instantiate the object at "path.in.model". If no class path is
            specified, or no type can be found for the class path in \'d\', then
            a Collection will be used as a placeholder.

            This is used to specify the type of a model or instance.
        loaded_ids
            A dictionary mapping ids to instances. This is used to ensure that
            all instances with the same id are the same object.

        Returns
        -------
        An instance
        """
        from SLE_Model_Autofit.SLE_Model_Mapper.SLE_Model_PriorModel.collection import (
            Collection,
        )
        from SLE_Model_Autofit.SLE_Model_Mapper.SLE_Model_PriorModel.prior_model import (
            Model,
        )
        from SLE_Model_Autofit.SLE_Model_Mapper.SLE_Model_Prior.abstract import Prior
        from SLE_Model_Autofit.SLE_Model_Mapper.SLE_Model_Prior.gaussian import (
            GaussianPrior,
        )
        from SLE_Model_Autofit.SLE_Model_Mapper.SLE_Model_Prior.tuple_prior import (
            TuplePrior,
        )
        from SLE_Model_Autofit.SLE_Model_Mapper.SLE_Model_Prior.SLE_Model_Arithmetic.compound import (
            Compound,
        )
        from SLE_Model_Autofit.SLE_Model_Mapper.SLE_Model_Prior.SLE_Model_Arithmetic.compound import (
            ModifiedPrior,
        )

        if isinstance(d, list):
            return [
                from_dict(
                    value,
                    reference=dereference(reference, str(index)),
                    loaded_ids=loaded_ids,
                )
                for (index, value) in enumerate(d)
            ]
        if not isinstance(d, dict):
            return d
        loaded_ids = {} if (loaded_ids is None) else loaded_ids
        type_ = d["type"]

        def get_class_path():
            try:
                return reference[""]
            except (KeyError, TypeError):
                return d.pop("class_path")

        if type_ == "model":
            class_path = get_class_path()
            try:
                instance = Model(get_class(class_path))
            except (ModuleNotFoundError, AttributeError):
                logger.warning(
                    f"Could not find type for class path {class_path}. Defaulting to Collection placeholder."
                )
                instance = Collection()
        elif type_ == "collection":
            instance = Collection()
        elif type_ == "tuple_prior":
            instance = TuplePrior()
        elif type_ == "compound":
            return Compound.from_dict(
                d, reference=dereference(reference, "assertion"), loaded_ids=loaded_ids
            )
        elif type_ == "modified":
            return ModifiedPrior.from_dict(
                d, reference=dereference(reference, "prior"), loaded_ids=loaded_ids
            )
        elif type_ == "dict":
            return {
                key: from_dict(
                    value, reference=dereference(reference, key), loaded_ids=loaded_ids
                )
                for (key, value) in d["arguments"].items()
                if value
            }
        elif type_ == "instance":
            class_path = get_class_path()
            try:
                cls_ = get_class(class_path)
                return cls_(
                    **{
                        key: from_dict(
                            value,
                            reference=dereference(reference, key),
                            loaded_ids=loaded_ids,
                        )
                        for (key, value) in d["arguments"].items()
                    }
                )
            except (ModuleNotFoundError, AttributeError):
                from autofit.mapper.model import ModelInstance

                logger.warning(
                    f"Could not find type for class path {class_path}. Defaulting to Instance placeholder."
                )
                instance = ModelInstance()
        elif type_ == "array":
            from autofit.mapper.prior_model.array import Array

            return Array.from_dict(d)
        else:
            try:
                return Prior.from_dict(d, loaded_ids=loaded_ids)
            except KeyError:
                cls_ = get_class(type_)
                instance = object.__new__(cls_)
        for (key, value) in d["arguments"].items():
            try:
                setattr(
                    instance,
                    key,
                    from_dict(
                        value,
                        reference=dereference(reference, key),
                        loaded_ids=loaded_ids,
                    ),
                )
            except KeyError:
                pass
        if "assertions" in d:
            instance.assertions = [
                from_dict(
                    value,
                    reference=dereference(reference, "assertions"),
                    loaded_ids=loaded_ids,
                )
                for value in d["assertions"]
            ]
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
        from SLE_Model_Autofit.SLE_Model_Mapper.SLE_Model_PriorModel.array import Array

        if isinstance(self, Collection):
            type_ = "collection"
        elif isinstance(self, AbstractPriorModel) and (self.prior_count == 0):
            type_ = "instance"
        elif isinstance(self, Model):
            type_ = "model"
        elif isinstance(self, TuplePrior):
            type_ = "tuple_prior"
        elif isinstance(self, Array):
            type_ = "array"
        else:
            raise AssertionError(
                f"{self.__class__.__name__} cannot be serialised to dict"
            )
        try:
            assertions = [assertion.dict() for assertion in self._assertions]
        except AttributeError:
            assertions = []
        dict_ = {"type": type_}
        if assertions:
            dict_["assertions"] = assertions
        arguments = {}
        for (key, value) in self._dict.items():
            try:
                value = to_dict(value)
            except AttributeError:
                pass
            except TypeError:
                pass
            arguments[key] = value
        dict_["arguments"] = arguments
        return dict_

    @property
    def _dict(self):
        return {
            key: value
            for (key, value) in self.__dict__.items()
            if (
                (key not in ("component_number", "item_number", "id", "cls", "label"))
                and (not key.startswith("_"))
            )
        }
