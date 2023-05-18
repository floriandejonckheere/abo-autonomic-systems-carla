from ai.carla import carla

import time


class Proximity:
    """
    Simple proximity sensor that detects objects in a given radius
    """

    def __init__(self, vehicle, x, y, z, r):
        self.vehicle = vehicle

        # Offset relative to vehicle
        self.x = x
        self.y = y
        self.z = z

        # Radius of the proximity sensor
        self.r = r

        self.last_render_at = 0

    def location(self):
        # Transform x, y, z offset to world coordinates
        vector = self.vehicle.get_transform().transform(carla.Location(x=self.x, y=self.y, z=self.z))

        return carla.Location(x=vector.x, y=vector.y, z=vector.z)

    def render(self, color=carla.Color(255, 0, 0)):
        if time.time() - self.last_render_at > 0.5:
            self.last_render_at = time.time()

            self.vehicle.get_world().debug.draw_point(self.location(), size=0.2, color=color, life_time=0.5)

    # FIXME: return distance to closest point, not to centroid
    def distance_to(self, obstacle):
        # Transform obstacle centroid to vehicle coordinates
        centroid = self.vehicle.get_transform().location + obstacle.centroid()

        self.vehicle.get_world().debug.draw_line(self.location(), centroid, thickness=0.5, color=carla.Color(255, 255, 0), life_time=0.1)

        return self.location().distance(centroid)
