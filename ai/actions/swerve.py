import numpy as np
import skfuzzy as fz

from .action import Action


class Swerve(Action):
    """Swerve to avoid an obstacle."""

    Left = -1.0
    Right = 1.0

    def __init__(self, direction, proximity):
        self.direction = direction
        self.proximity = proximity

        # Universe variables
        self.x_proximity = np.arange(0, 1000, 1)

        # Fuzzy membership functions
        self.prox_lo = fz.zmf(self.x_proximity, 0, 30)

    def apply(self, control):
        # Set steering
        control.steer = self.calculate_steer()

    def calculate_steer(self):
        # Steer is inverse proportional to the proximity
        steer = fz.interp_membership(self.x_proximity, self.prox_lo, self.proximity)

        # Steer in right direction
        steer *= self.direction

        # Limit to realistic bounds
        return np.clip(steer, -0.7, 0.7)
