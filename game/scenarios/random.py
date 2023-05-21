from collections import deque

import random

from ai.carla import carla

from .scenario import Scenario


# TODO: Make an 'intelligent' list of targets where cars could go (has annotated waypoints so you could use that)
class Random(Scenario):
    """Random scenario."""

    # List of parking spaces in format (x, y, yaw)
    parking = [
        # Street parking (parallel)
        *[(x, -10.8, 180) for x in range(50, 61, 5)],
        *[(x, -9, 180) for x in range(175, 216, 5)],
        *[(x, -10.1, 180) for x in range(95, 136, 5)],
        *[(x, 11.5, 0) for x in range(50, 216, 5)],
        *[(-12.8, y, 90) for y in range(45, 116, 5)],
        *[(8.5, y, -90) for y in range(55, 116, 5)],

        # Private parking on driveway
        (31.9, 119.5, 92),
        (45.9, 116.3, 92),
        (63.4, 152.5, 92),
        (73.8, 147.8, 92),
        (69.8, 114.5, 92),
        (97.6, 116.4, 92),
        (171.6, 134.3, -135),
        (177.6, 134.3, -135),
        (-161.1, 31.8, 0),

        # Private parking on double driveway
        (-162.3, 23.4, 0),
        (-162.3, 17.3, 0),

        # On curb in front of building
        (-134.6, -18.0, -90),

        # Garage boxes
        (-148.2, 154.7, 90),
        (-111.6, 67.1, 180),

        # Large parking lots or empty spaces
        (-97.4, 234.2, 70),
        (-113.2, 105.1, 90),

        # Behind market stalls
        (-108.2, -25.3, -90),
    ]

    def __init__(self, world, length=5):
        super().__init__(world)

        # Set random parking space as first waypoint
        self.waypoints = deque([self.random_parking()])

        # Generate length-2 random waypoints
        for _ in range(length - 2):
            self.waypoints.append(random.choice(world.get_map().get_spawn_points()))

        # Add a random parking space as the last waypoint
        self.waypoints.append(self.random_parking())

    def random_parking(self):
        x, y, yaw = random.choice(self.parking)

        return carla.Transform(carla.Location(x=x, y=y), carla.Rotation(yaw=yaw))
