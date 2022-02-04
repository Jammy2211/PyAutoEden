from typing import List
from SHE_SLModel_Autogalaxy import exc
from SHE_SLModel_Autogalaxy.SHE_SLModel_Profiles.SHE_SLModel_MassProfiles import (
    MassProfile,
)
from SHE_SLModel_Autogalaxy.SHE_SLModel_Profiles.SHE_SLModel_MassProfiles.dark_mass_profiles import (
    DarkProfile,
)
from SHE_SLModel_Autogalaxy.SHE_SLModel_Profiles.SHE_SLModel_MassProfiles.stellar_mass_profiles import (
    StellarProfile,
)


class StellarDarkDecomp:
    def __init__(self, galaxy):
        self.galaxy = galaxy

    @property
    def mass_profile_list(self):
        return self.galaxy.mass_profile_list

    @property
    def has_stellar_profile(self):
        return len(self.stellar_profile_list) > 0

    @property
    def has_dark_profile(self):
        return len(self.dark_profile_list) > 0

    @property
    def stellar_profile_list(self):
        return [
            profile
            for profile in self.mass_profile_list
            if isinstance(profile, StellarProfile)
        ]

    @property
    def dark_profile_list(self):
        return [
            profile
            for profile in self.mass_profile_list
            if isinstance(profile, DarkProfile)
        ]

    def stellar_mass_angular_within_circle_from(self, radius):
        if self.has_stellar_profile:
            return sum(
                [
                    profile.mass_angular_within_circle_from(radius=radius)
                    for profile in self.stellar_profile_list
                ]
            )
        else:
            raise exc.GalaxyException(
                "You cannot perform a stellar mass-based calculation on a galaxy which does not have a stellar mass-profile "
            )

    def dark_mass_angular_within_circle_from(self, radius):
        if self.has_dark_profile:
            return sum(
                [
                    profile.mass_angular_within_circle_from(radius=radius)
                    for profile in self.dark_profile_list
                ]
            )
        else:
            raise exc.GalaxyException(
                "You cannot perform a dark mass-based calculation on a galaxy which does not have a dark mass-profile"
            )

    def stellar_fraction_at_radius_from(self, radius):
        return 1.0 - self.dark_fraction_at_radius_from(radius=radius)

    def dark_fraction_at_radius_from(self, radius):
        stellar_mass = self.stellar_mass_angular_within_circle_from(radius=radius)
        dark_mass = self.dark_mass_angular_within_circle_from(radius=radius)
        return dark_mass / (stellar_mass + dark_mass)
