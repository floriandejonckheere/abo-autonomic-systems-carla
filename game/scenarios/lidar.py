from ai.carla import carla

from .scenario import Scenario

import game.utils as utils


class Lidar(Scenario):
    """LIDAR test scenario."""

    waypoints = [
        carla.Location(-6.5, 50.9, 1.8431),
        carla.Location(-5.4, 187.0, 1.8431),
    ]

    def __init__(self, world):
        super().__init__(world)

        self.use_spawnpoint = False

    def setup(self):
        locations = [
            carla.Location(-6.5, 61.6, 1.8431),
            carla.Location(-10, 61.6, 1.8431),
            carla.Location(-10, 55, 1.8431),
        ]

        for location in locations:
            spawn_point = carla.Transform(location=location,  rotation=carla.Rotation(yaw=90))

            car = utils.try_spawn_random_vehicle_at(self.world, spawn_point)
            self.actors.append(car)
