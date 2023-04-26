import numpy as np
import skfuzzy as fz

from .action import Action


class Steer(Action):
    """Steer based on the angle to the waypoint"""

    def __init__(self, knowledge):
        super().__init__(knowledge)

        # Universe variables
        self.x_angle = np.arange(-180, 180, 1)

        # Fuzzy membership functions
        self.steer_hi = fz.smf(self.x_angle, -80, 80)

    def apply(self, control):
        # Set steering
        control.steer = self.calculate_steer()

    def calculate_steer(self):
        # Steer is proportional to the angle
        steer = fz.interp_membership(self.x_angle, self.steer_hi, self.knowledge.angle_to_waypoint())

        # Rescale to [-1, 1]
        steer = (steer - 0.5) * 2

        # Limit to 70% of the maximum steering angle
        return 0.7 * steer
