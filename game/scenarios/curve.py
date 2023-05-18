from ai.carla import carla

from .scenario import Scenario


class Curve(Scenario):
    """Across a curved road."""

    def __init__(self, world):
        super().__init__(world)

        self.use_spawnpoint = False

    waypoints = [
        carla.Location(229.6, 60.4, 1.8431),
        carla.Location(5.5, 183.5, 1.8431),
    ]
