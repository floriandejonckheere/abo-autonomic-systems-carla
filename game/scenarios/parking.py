from ai.carla import carla

from .scenario import Scenario


class Parking(Scenario):
    """From street parking to a private parking."""

    WAYPOINTS = [
        carla.Location(x=-12.6, y=80.8, z=1.8),
        carla.Location(x=63.4, y=152.5, z=1.8),
    ]

    def __init__(self, world):
        super().__init__(world)

        self.use_spawnpoint = False
