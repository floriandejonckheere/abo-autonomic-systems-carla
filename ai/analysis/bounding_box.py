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

    def render(self, world, color=carla.Color(255, 0, 0)):
            world.debug.draw_line(
                carla.Location(self.x_min, self.y_min, self.z_min),
                carla.Location(self.x_min, self.y_min, self.z_max), life_time=1, color=color)
            world.debug.draw_line(
                carla.Location(self.x_min, self.y_max, self.z_min),
                carla.Location(self.x_min, self.y_max, self.z_max), life_time=1, color=color)
            world.debug.draw_line(
                carla.Location(self.x_max, self.y_min, self.z_min),
                carla.Location(self.x_max, self.y_min, self.z_max), life_time=1, color=color)
            world.debug.draw_line(
                carla.Location(self.x_max, self.y_max, self.z_min),
                carla.Location(self.x_max, self.y_max, self.z_max), life_time=1, color=color)

            world.debug.draw_line(
                carla.Location(self.x_min, self.y_min, self.z_min),
                carla.Location(self.x_max, self.y_min, self.z_min), life_time=1, color=color)
            world.debug.draw_line(
                carla.Location(self.x_min, self.y_min, self.z_max),
                carla.Location(self.x_max, self.y_min, self.z_max), life_time=1, color=color)
            world.debug.draw_line(
                carla.Location(self.x_min, self.y_max, self.z_min),
                carla.Location(self.x_max, self.y_max, self.z_min), life_time=1, color=color)
            world.debug.draw_line(
                carla.Location(self.x_min, self.y_max, self.z_max),
                carla.Location(self.x_max, self.y_max, self.z_max), life_time=1, color=color)

            world.debug.draw_line(
                carla.Location(self.x_min, self.y_min, self.z_min),
                carla.Location(self.x_min, self.y_max, self.z_min), life_time=1, color=color)
            world.debug.draw_line(
                carla.Location(self.x_min, self.y_min, self.z_max),
                carla.Location(self.x_min, self.y_max, self.z_max), life_time=1, color=color)
            world.debug.draw_line(
                carla.Location(self.x_max, self.y_min, self.z_min),
                carla.Location(self.x_max, self.y_max, self.z_min), life_time=1, color=color)
            world.debug.draw_line(
                carla.Location(self.x_max, self.y_min, self.z_max),
                carla.Location(self.x_max, self.y_max, self.z_max), life_time=1, color=color)
