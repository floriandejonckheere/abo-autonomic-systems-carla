from ai.carla import carla

import math
import time


class Proximity:
    """
    Simple proximity sensor that detects objects in a given radius
    """

    def __init__(self, vehicle, x, y, z, r, color=carla.Color(255, 0, 0)):
        self.vehicle = vehicle

        # Offset relative to vehicle
        self.x = x
        self.y = y
        self.z = z

        # Radius of the proximity sensor
        self.r = r

        self.color = color

        self.last_render_at = 0

    def location(self):
        # Transform x, y, z offset to world coordinates
        vector = self.vehicle.get_transform().transform(carla.Location(x=self.x, y=self.y, z=self.z))

        return carla.Location(x=vector.x, y=vector.y, z=vector.z)

    def render(self):
        if time.time() - self.last_render_at > 0.5:
            self.last_render_at = time.time()

            self.vehicle.get_world().debug.draw_point(self.location(), size=0.2, color=self.color, life_time=0.5)

    def distance_to(self, obstacle):
        # x = min(max(self.x, obstacle.x_min), obstacle.x_max)
        # y = min(max(self.y, obstacle.y_min), obstacle.y_max)
        # z = min(max(self.z, obstacle.z_min), obstacle.z_max)

        # point = self.vehicle.get_transform().location + carla.Location(x=x, y=y, z=z)

        # Transform obstacle centroid to vehicle coordinates
        centroid = self.vehicle.get_transform().location + obstacle.centroid()

        # self.vehicle.get_world().debug.draw_point(centroid, size=0.2, color=carla.Color(255, 255, 0), life_time=0.1)
        # self.vehicle.get_world().debug.draw_point(point, size=0.2, color=self.color, life_time=0.1)

        # self.vehicle.get_world().debug.draw_line(self.location(), centroid, thickness=0.1, color=carla.Color(255, 255, 0), life_time=0.1)
        # self.vehicle.get_world().debug.draw_line(self.location(), point, thickness=0.1, color=carla.Color(255, 0, 0), life_time=0.1)

        # print(f'c={self.location().distance(centroid):.2f} d={distance:.2f}')

        return self.location().distance(centroid)
