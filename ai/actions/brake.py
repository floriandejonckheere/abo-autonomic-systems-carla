import numpy as np
import skfuzzy as fz

from .action import Action


class Brake(Action):
    """Apply brake based on distance to a waypoint"""

    def __init__(self, source, target):
        self.source = source
        self.target = target

        # Universe variables
        self.x_distance = np.arange(0, 101, 1)

        # Fuzzy membership functions
        self.dist_lo = fz.zmf(self.x_distance, 0.1, 2)
        self.dist_hi = fz.smf(self.x_distance, 0.1, 2)

    def apply(self, control):
        # Set throttle and brake
        control.throttle = 0.0
        control.brake = self.calculate_brake()

    def calculate_brake(self):
        # Brake is proportional to the distance
        return fz.interp_membership(self.x_distance, self.dist_hi, self.source.distance(self.target))
