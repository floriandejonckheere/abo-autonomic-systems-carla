from ai.carla import carla

from .scenario import Scenario


class MilestoneTwo(Scenario):
    """Drive to the gas station"""

    waypoints = [
        carla.Location(-35.2, 177.7, 1.8431),
        carla.Location(-30, 167, 1.8431),
    ]
