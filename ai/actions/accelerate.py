import numpy as np
import skfuzzy as fz

from .action import Action


class Accelerate(Action):
    """Apply throttle and release brake based on distance"""

    def __init__(self, distance):
        self.distance = distance

        # Universe variables
        self.x_distance = np.arange(0, 1000, 1)

        # Fuzzy membership functions
        self.dist_lo = fz.zmf(self.x_distance, 0.2, 3)
        self.dist_hi = fz.smf(self.x_distance, 0.2, 3)

    def apply(self, control):
        # Set throttle and brake
        control.throttle = self.calculate_throttle()
        control.brake = 0.0

    def calculate_throttle(self):
        # Throttle is proportional to the distance
        return fz.interp_membership(self.x_distance, self.dist_hi, self.distance)
