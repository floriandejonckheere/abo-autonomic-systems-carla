import numpy as np
import skfuzzy as fz


class Fuzzy:
    def __init__(self):
        # Initialize values
        self.distance = 0.0
        self.speed = 0.0
        self.target_speed = 0.0
        self.angle = 0.0

        # Universe variables
        self.x_distance = np.arange(0, 101, 1)
        self.x_speed = np.arange(0, 101, 1)
        self.x_target_speed = np.arange(0, 101, 1)
        self.x_angle = np.arange(-180, 180, 1)

        # Fuzzy membership functions
        self.dist_lo = fz.zmf(self.x_distance, 0.5, 2)
        self.dist_hi = fz.smf(self.x_distance, 0.5, 2)
        self.speed_hi = fz.smf(self.x_speed, 7, 9)

        self.steer_hi = fz.smf(self.x_angle, -90, 90)

    def update(self, distance, speed, target_speed, angle):
        self.distance = distance
        self.speed = speed
        self.target_speed = target_speed
        self.angle = angle

    def get_throttle(self):
        # Throttle is proportional to the distance
        dst = fz.interp_membership(self.x_distance, self.dist_hi, self.distance)

        # Modifier to the throttle based on speed relative to the speed target_speed
        spd = fz.interp_membership(self.x_speed, self.speed_hi, self.target_speed - self.speed)

        return dst * spd

    def get_brake(self):
        # return 0.6 * fz.interp_membership(self.x_distance, self.dist_lo, self.distance)
        return 0.0

    def get_steer(self):
        # Steer is proportional to the angle
        steer = fz.interp_membership(self.x_angle, self.steer_hi, self.angle)

        # Rescale to [-1, 1]
        steer = (steer - 0.5) * 2

        # Limit to 70% of the maximum steering angle
        return 0.7 * steer
