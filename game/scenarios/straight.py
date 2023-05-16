from ai.carla import carla

from .scenario import Scenario


class Straight(Scenario):
    """Straight ahead"""

    waypoints = [
        carla.Location(37.2, 3.4, 1.8431),
        carla.Location(218.2, 5.9, 1.8431),
    ]
