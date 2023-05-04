import numpy as np
import skfuzzy as fz

from .action import Action


class Cruise(Action):
    """Stop-and-go based on proximity and speed"""

    def __init__(self, proximity, speed):
        self.proximity = proximity
        self.speed = speed

        # Universe variables
        self.x_proximity = np.arange(0, 1000, 1)

        # Fuzzy membership functions
        self.prox_lo = fz.zmf(self.x_proximity, 40, 80)
        self.prox_hi = fz.smf(self.x_proximity, 40, 80)

    def apply(self, control):
        # Set throttle and brake
        control.throttle *= self.calculate_throttle()
        control.brake *= self.calculate_brake()

    def calculate_throttle(self):
        # Throttle is inverse proportional to the distance
        return fz.interp_membership(self.x_proximity, self.prox_hi, self.proximity)

    def calculate_brake(self):
        # Brake is proportional to the distance
        return fz.interp_membership(self.x_proximity, self.prox_lo, self.proximity)
