from ai.carla import carla

from .scenario import Scenario


class MilestoneFour(Scenario):
    """Drive to the gas station."""

    waypoints = [
        carla.Location(42.5959, -4.3443, 1.8431),
        carla.Location(134, -3, 1.8431),
    ]
