from ai.carla import carla

from .scenario import Scenario


class MilestoneTwo(Scenario):
    """Drive to the gas station."""

    waypoints = [
        carla.Location(42.5959, -4.3443, 1.8431),
        carla.Location(-30, 167, 1.8431),
    ]
