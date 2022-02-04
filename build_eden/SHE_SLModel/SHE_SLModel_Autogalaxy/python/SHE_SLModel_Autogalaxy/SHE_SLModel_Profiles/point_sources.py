from typing import Tuple


class Point:
    def __init__(self, centre=(0.0, 0.0)):
        self.centre = centre


class PointSourceChi(Point):
    def __init__(self, centre=(0.0, 0.0)):
        super().__init__(centre=centre)


class PointFlux(Point):
    def __init__(self, centre=(0.0, 0.0), flux=0.1):
        super().__init__(centre=centre)
        self.flux = flux
