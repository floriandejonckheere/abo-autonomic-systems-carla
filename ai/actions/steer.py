import numpy as np
import skfuzzy as fz

from .action import Action


class Steer(Action):
    """Steer based on the angle to a waypoint"""

    def __init__(self, source, target):
        self.source = source
        self.target = target

        # Universe variables
        self.x_angle = np.arange(-180, 180, 1)

        # Fuzzy membership functions
        self.steer_hi = fz.smf(self.x_angle, -80, 80)

    def apply(self, control):
        # Set steering
        control.steer = self.calculate_steer()

    def calculate_steer(self):
        # Steer is proportional to the angle
        steer = fz.interp_membership(self.x_angle, self.steer_hi, self.angle_to_waypoint())

        # Rescale to [-1, 1]
        steer = (steer - 0.5) * 2

        # Limit to 70% of the maximum steering angle
        return 0.7 * steer

    def angle_to_waypoint(self):
        # Normalize source and target vectors
        source_vector = [self.source.x, self.source.y]
        source_vector /= np.linalg.norm(source_vector)

        target_vector = [self.target.x, self.target.y]
        target_vector /= np.linalg.norm(target_vector)

        # Calculate dot product between vectors
        dot_product = np.dot(source_vector, target_vector)

        # Calculate cross product between vectors
        cross_product = np.cross(source_vector, target_vector)

        # Calculate angle in radians
        angle_radians = np.arccos(dot_product)

        # Determine direction of angle using cross product
        if cross_product < 0:
            angle_radians = -angle_radians

        # Convert angle from radians to degrees
        return np.degrees(angle_radians)
