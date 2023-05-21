from ai.carla import carla

from .scenario import Scenario


class TrafficLights(Scenario):
    """Straight towards the traffic lights, stop if necessary."""

    WAYPOINTS = [
        carla.Location(-6.2, 95.6, 1.8431),
        carla.Location(-5.4, 187.0, 1.8431),
        carla.Location(-42.7, 196.9, 1.8431),
    ]

    def __init__(self, world):
        super().__init__(world)

        self.use_spawnpoint = False
