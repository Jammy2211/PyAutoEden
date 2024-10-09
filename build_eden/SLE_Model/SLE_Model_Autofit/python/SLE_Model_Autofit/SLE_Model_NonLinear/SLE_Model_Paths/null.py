import tempfile
from typing import Optional
from SLE_Model_Autofit.SLE_Model_NonLinear.SLE_Model_Paths.abstract import AbstractPaths


class NullPaths(AbstractPaths):
    """
    Null version of paths object for avoiding writing of files to disk
    """

    def __init__(self):
        super().__init__()
        self.objects = dict()
        self._samples_path = tempfile.mkdtemp()

    def save_summary(self, samples, log_likelihood_function_time):
        pass

    @property
    def samples_path(self):
        return self._samples_path

    @AbstractPaths.parent.setter
    def parent(self, parent):
        pass

    @property
    def is_grid_search(self):
        return False

    def create_child(
        self, name=None, path_prefix=None, is_identifier_in_paths=None, identifier=None
    ):
        return NullPaths()

    def save_named_instance(self, name, instance):
        pass

    def save_object(self, name, obj):
        self.objects[name] = obj

    def load_object(self, name):
        return self.objects[name]

    def remove_object(self, name):
        pass

    def is_object(self, name):
        pass

    @property
    def is_complete(self):
        return False

    def completed(self):
        pass

    def save_all(self, search_config_dict, info, pickle_files):
        pass

    def load_samples(self):
        pass

    def save_samples(self, samples):
        pass

    def load_samples_info(self):
        pass
