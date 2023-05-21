from ai.carla import carla

from .scenario import Scenario


class MilestoneOne(Scenario):
    """Straight towards the roundabout, then enter and drive a bit."""

    WAYPOINTS = [
        carla.Location(42.5959, -4.3443, 1.8431),
        carla.Location(22, -4, 1.8431),
        carla.Location(9, -22, 1.8431),
    ]
