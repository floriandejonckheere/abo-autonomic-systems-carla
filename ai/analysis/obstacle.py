from ai.carla import carla

import time


class Obstacle:
    """Potential obstacle, delimited by a bounding box in 3D space."""

    def __init__(self, x_min, y_min, z_min, x_max, y_max, z_max):
        self.x_min = x_min
        self.y_min = y_min
        self.z_min = z_min

        self.x_max = x_max
        self.y_max = y_max
        self.z_max = z_max

        # FIXME: remove this
        if x_min > x_max:
            raise ValueError('x_min must be less than x_max')

        if y_min > y_max:
            raise ValueError('y_min must be less than y_max')

        if z_min > z_max:
            raise ValueError('z_min must be less than z_max')

        self.last_render_at = 0

    def centroid(self):
        return carla.Location((self.x_min + self.x_max) / 2, (self.y_min + self.y_max) / 2, (self.z_min + self.z_max) / 2)

    def volume(self):
        return (self.x_max - self.x_min) * (self.y_max - self.y_min) * (self.z_max - self.z_min)

    def overlaps_with(self, other):
        return self.x_max > other.x_min and self.x_min < other.x_max and self.y_max > other.y_min and self.y_min < other.y_max and self.z_max > other.z_min and self.z_min < other.z_max

    def render(self, vehicle, color=carla.Color(255, 0, 0), life_time=0.5):
        if time.time() - self.last_render_at < life_time:
            return

        self.last_render_at = time.time()

        debug = vehicle.get_world().debug

        # Translate coordinates to vehicle location
        location = vehicle.get_location()

        debug.draw_line(
            carla.Location(self.x_min, self.y_min, self.z_min) + location,
            carla.Location(self.x_min, self.y_min, self.z_max) + location, life_time=life_time, color=color)
        debug.draw_line(
            carla.Location(self.x_min, self.y_max, self.z_min) + location,
            carla.Location(self.x_min, self.y_max, self.z_max) + location, life_time=life_time, color=color)
        debug.draw_line(
            carla.Location(self.x_max, self.y_min, self.z_min) + location,
            carla.Location(self.x_max, self.y_min, self.z_max) + location, life_time=life_time, color=color)
        debug.draw_line(
            carla.Location(self.x_max, self.y_max, self.z_min) + location,
            carla.Location(self.x_max, self.y_max, self.z_max) + location, life_time=life_time, color=color)

        debug.draw_line(
            carla.Location(self.x_min, self.y_min, self.z_min) + location,
            carla.Location(self.x_max, self.y_min, self.z_min) + location, life_time=life_time, color=color)
        debug.draw_line(
            carla.Location(self.x_min, self.y_min, self.z_max) + location,
            carla.Location(self.x_max, self.y_min, self.z_max) + location, life_time=life_time, color=color)
        debug.draw_line(
            carla.Location(self.x_min, self.y_max, self.z_min) + location,
            carla.Location(self.x_max, self.y_max, self.z_min) + location, life_time=life_time, color=color)
        debug.draw_line(
            carla.Location(self.x_min, self.y_max, self.z_max) + location,
            carla.Location(self.x_max, self.y_max, self.z_max) + location, life_time=life_time, color=color)

        debug.draw_line(
            carla.Location(self.x_min, self.y_min, self.z_min) + location,
            carla.Location(self.x_min, self.y_max, self.z_min) + location, life_time=life_time, color=color)
        debug.draw_line(
            carla.Location(self.x_min, self.y_min, self.z_max) + location,
            carla.Location(self.x_min, self.y_max, self.z_max) + location, life_time=life_time, color=color)
        debug.draw_line(
            carla.Location(self.x_max, self.y_min, self.z_min) + location,
            carla.Location(self.x_max, self.y_max, self.z_min) + location, life_time=life_time, color=color)
        debug.draw_line(
            carla.Location(self.x_max, self.y_min, self.z_max) + location,
            carla.Location(self.x_max, self.y_max, self.z_max) + location, life_time=life_time, color=color)
