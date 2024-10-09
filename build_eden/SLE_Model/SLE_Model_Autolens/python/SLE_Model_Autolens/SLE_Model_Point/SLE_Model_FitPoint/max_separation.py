from typing import Optional
import SLE_Model_Autoarray as aa
from SLE_Model_Autolens.SLE_Model_Lens.ray_tracing import Tracer


class AbstractFitPositionsSourcePlane:
    def __init__(self, positions, noise_map, tracer):
        """
        Given a positions dataset, which is a list of positions with names that associated them to model source
        galaxies, use a `Tracer` to determine the traced coordinate positions in the source-plane.

        Different children of this abstract class are available which use the traced coordinates to define a chi-squared
        value in different ways.

        Parameters
        ----------
        positions : Grid2DIrregular
            The (y,x) arc-second coordinates of named positions which the log_likelihood is computed using. Positions
            are paired to galaxies in the `Tracer` using their names.
        tracer : Tracer
            The object that defines the ray-tracing of the strong lens system of galaxies.
        noise_value
            The noise-value assumed when computing the log likelihood.
        """
        self.positions = positions
        self.noise_map = noise_map
        self.source_plane_positions = tracer.traced_grid_2d_list_from(grid=positions)[
            (-1)
        ]

    @property
    def furthest_separations_of_source_plane_positions(self):
        """
        Returns the furthest distance of every source-plane (y,x) coordinate to the other source-plane (y,x)
        coordinates.

        For example, for the following source-plane positions:

        source_plane_positions = [[(0.0, 0.0), (0.0, 1.0), (0.0, 3.0)]

        The returned furthest distances are:

        source_plane_positions = [3.0, 2.0, 3.0]

        Returns
        -------
        aa.ArrayIrregular
            The further distances of every set of grouped source-plane coordinates the other source-plane coordinates
            that it is grouped with.
        """
        return self.source_plane_positions.furthest_distances_to_other_coordinates

    @property
    def max_separation_of_source_plane_positions(self):
        return max(self.furthest_separations_of_source_plane_positions)

    def max_separation_within_threshold(self, threshold):
        return self.max_separation_of_source_plane_positions <= threshold


class FitPositionsSourceMaxSeparation(AbstractFitPositionsSourcePlane):
    def __init__(self, positions, noise_map, tracer):
        """A lens position fitter, which takes a set of positions (e.g. from a plane in the tracer) and computes         their maximum separation, such that points which tracer closer to one another have a higher log_likelihood.

        Parameters
        ----------
        positions : Grid2DIrregular
            The (y,x) arc-second coordinates of positions which the maximum distance and log_likelihood is computed using.
        noise_value
            The noise-value assumed when computing the log likelihood.
        """
        super().__init__(positions=positions, noise_map=noise_map, tracer=tracer)
