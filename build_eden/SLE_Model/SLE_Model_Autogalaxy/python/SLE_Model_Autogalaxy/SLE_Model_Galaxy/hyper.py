from itertools import count

"""
This class is depreciated but here to retain backwards compatibility with older scripts.
"""


class HyperGalaxy:
    _ids = count()

    def __init__(self, contribution_factor=0.0, noise_factor=0.0, noise_power=1.0):
        self.contribution_factor = contribution_factor
        self.noise_factor = noise_factor
        self.noise_power = noise_power
        self.component_number = next(self._ids)
