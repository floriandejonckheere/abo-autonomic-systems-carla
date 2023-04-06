import numpy as np
import skfuzzy as fz


class Fuzzy:
    def __init__(self):
        self.distance = 0.0

        # Universe variables
        self.x_distance = np.arange(0, 101, 1)

        # Fuzzy membership functions
        self.dist_lo = fz.trapmf(self.x_distance, [0, 0, 10, 20])
        self.dist_hi = fz.trapmf(self.x_distance, [10, 20, 100, 100])

    def update(self, distance):
        self.distance = distance

    def get_throttle(self):
        return fz.interp_membership(self.x_distance, self.dist_hi, self.distance)

    def get_brake(self):
        return fz.interp_membership(self.x_distance, self.dist_lo, self.distance)
