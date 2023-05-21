from ai.carla import carla

from .scenario import Scenario


class Straight(Scenario):
    """Straight ahead."""

    WAYPOINTS = [
        carla.Location(37.2, 4.4, 1.8431),
        carla.Location(100.2, 4.4, 1.8431),
    ]
