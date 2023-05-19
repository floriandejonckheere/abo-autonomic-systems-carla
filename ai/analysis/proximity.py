import math


class Proximity:
    """Simple proximity sensor that detects objects in a given radius."""

    def __init__(self, vehicle, x, y, z):
        self.vehicle = vehicle

        # Offset relative to vehicle
        self.x = x
        self.y = y
        self.z = z

    def distance_to(self, obstacle):
        x_min = obstacle.y_min
        y_min = obstacle.x_min
        z_min = obstacle.z_min

        x_max = obstacle.y_max
        y_max = obstacle.x_max
        z_max = obstacle.z_max

        # Check if the point is inside the cube
        if x_min <= self.x <= x_max and y_min <= self.y <= y_max and z_min <= self.z <= z_max:
            return 0.0

        # Calculate the distance to the cube's surfaces along each axis
        dx = max(0, x_min - self.x, self.x - x_max)
        dy = max(0, y_min - self.y, self.y - y_max)
        dz = max(0, z_min - self.z, self.z - z_max)

        # Calculate the Euclidean distance between the point and the cube's surfaces
        distance = math.sqrt(dx ** 2 + dy ** 2 + dz ** 2)

        return distance
