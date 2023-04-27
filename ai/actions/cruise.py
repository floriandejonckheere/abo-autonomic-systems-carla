import numpy as np
import skfuzzy as fz

from .action import Action


class Cruise(Action):
    """Stop-and-go based on proximity"""

    def __init__(self, proximity):
        self.proximity = proximity

        # Universe variables
        self.x_proximity = np.arange(0, 1000, 1)

        # Fuzzy membership functions
        self.prox_lo = fz.zmf(self.x_proximity, 40, 80)
        self.prox_hi = fz.smf(self.x_proximity, 40, 80)

    def apply(self, control):
        # Set brake
        control.brake = self.calculate_brake()

        # If brake is not applied, set throttle
        if control.brake > 0.05:
            control.throttle = 0.0

    def calculate_brake(self):
        # Brake is proportional to the distance
        return fz.interp_membership(self.x_proximity, self.prox_lo, self.proximity)
