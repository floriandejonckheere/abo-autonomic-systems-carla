from ai.carla import carla


class BoundingBox:
    """Bounding box delimiting an object in 3D space."""

    def __init__(self, x_min, y_min, z_min, x_max, y_max, z_max):
        self.x_min = x_min
        self.y_min = y_min
        self.z_min = z_min

        self.x_max = x_max
        self.y_max = y_max
        self.z_max = z_max

    def render(self, vehicle, color=carla.Color(255, 0, 0)):
        debug = vehicle.get_world().debug

        # Translate coordinates to vehicle location
        location = vehicle.get_location()

        debug.draw_line(
            carla.Location(self.x_min, self.y_min, self.z_min) + location,
            carla.Location(self.x_min, self.y_min, self.z_max) + location, life_time=1, color=color)
        debug.draw_line(
            carla.Location(self.x_min, self.y_max, self.z_min) + location,
            carla.Location(self.x_min, self.y_max, self.z_max) + location, life_time=1, color=color)
        debug.draw_line(
            carla.Location(self.x_max, self.y_min, self.z_min) + location,
            carla.Location(self.x_max, self.y_min, self.z_max) + location, life_time=1, color=color)
        debug.draw_line(
            carla.Location(self.x_max, self.y_max, self.z_min) + location,
            carla.Location(self.x_max, self.y_max, self.z_max) + location, life_time=1, color=color)

        debug.draw_line(
            carla.Location(self.x_min, self.y_min, self.z_min) + location,
            carla.Location(self.x_max, self.y_min, self.z_min) + location, life_time=1, color=color)
        debug.draw_line(
            carla.Location(self.x_min, self.y_min, self.z_max) + location,
            carla.Location(self.x_max, self.y_min, self.z_max) + location, life_time=1, color=color)
        debug.draw_line(
            carla.Location(self.x_min, self.y_max, self.z_min) + location,
            carla.Location(self.x_max, self.y_max, self.z_min) + location, life_time=1, color=color)
        debug.draw_line(
            carla.Location(self.x_min, self.y_max, self.z_max) + location,
            carla.Location(self.x_max, self.y_max, self.z_max) + location, life_time=1, color=color)

        debug.draw_line(
            carla.Location(self.x_min, self.y_min, self.z_min) + location,
            carla.Location(self.x_min, self.y_max, self.z_min) + location, life_time=1, color=color)
        debug.draw_line(
            carla.Location(self.x_min, self.y_min, self.z_max) + location,
            carla.Location(self.x_min, self.y_max, self.z_max) + location, life_time=1, color=color)
        debug.draw_line(
            carla.Location(self.x_max, self.y_min, self.z_min) + location,
            carla.Location(self.x_max, self.y_max, self.z_min) + location, life_time=1, color=color)
        debug.draw_line(
            carla.Location(self.x_max, self.y_min, self.z_max) + location,
            carla.Location(self.x_max, self.y_max, self.z_max) + location, life_time=1, color=color)
