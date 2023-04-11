import numpy as np
import skfuzzy as fz


class Fuzzy:
    def __init__(self):
        # Initialize values
        self.distance = 0.0
        self.speed = 0.0
        self.target_speed = 0.0

        # Universe variables
        self.x_distance = np.arange(0, 101, 1)
        self.x_speed = np.arange(0, 101, 1)
        self.x_target_speed = np.arange(0, 101, 1)

        # Fuzzy membership functions
        self.dist_lo = fz.zmf(self.x_distance, 5, 15)
        self.dist_hi = fz.smf(self.x_distance, 5, 15)
        self.speed_hi = fz.smf(self.x_speed, 4, 5)

    def update(self, distance, speed, target_speed):
        self.distance = distance
        self.speed = speed
        self.target_speed = target_speed

    def get_throttle(self):
        # Throttle is proportional to the distance
        t1 = fz.interp_membership(self.x_distance, self.dist_hi, self.distance)

        # Modifier to the throttle based on speed relative to the speed target_speed
        t2 = fz.interp_membership(self.x_speed, self.speed_hi, self.target_speed - self.speed)

        # print(f'{self.speed:.2f}/{self.target_speed:.2f} => ({t1:.2f}, {t2:.2f})')

        return t1 * t2

    def get_brake(self):
        # return 0.6 * fz.interp_membership(self.x_distance, self.dist_lo, self.distance)
        return 0.0