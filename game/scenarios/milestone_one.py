from ai.carla import carla

from .scenario import Scenario


class MilestoneOne(Scenario):
    """Straight towards the roundabout, then enter and drive a bit"""

    waypoints = [
        carla.Location(42.5959, -4.3443, 1.8431),
        carla.Location(18.3, -4.6, 1.8431),
        carla.Location(9, -31, 1.8431),
    ]
