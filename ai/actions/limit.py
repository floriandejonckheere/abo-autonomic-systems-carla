import numpy as np
import skfuzzy as fz

from .action import Action


class Limit(Action):
    """Limit the throttle based on the current target speed (speed limit)"""

    def __init__(self, knowledge):
        super().__init__(knowledge)

        # Universe variables
        self.x_speed = np.arange(0, 101, 1)
        self.x_target_speed = np.arange(0, 101, 1)

        # Fuzzy membership functions
        self.speed_hi = fz.smf(self.x_speed, 3, 5)

    def apply(self, control):
        # Update throttle
        control.throttle *= self.calculate_throttle()

    def calculate_throttle(self):
        # Modifier to the throttle based on speed relative to the speed target_speed
        return fz.interp_membership(self.x_speed, self.speed_hi, self.knowledge.target_speed - self.knowledge.speed())
