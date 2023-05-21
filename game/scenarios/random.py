from collections import deque

import random

from ai.carla import carla

from .scenario import Scenario


# TODO: Make an 'intelligent' list of targets where cars could go (has annotated waypoints so you could use that)
# TODO, BONUS: Make fixed exit and entry points (for example parking lots),
# so that cars are removed from simulation when they enter those and new ones are created from random points.
class Random(Scenario):
    """Random scenario."""

    def __init__(self, world, length=5):
        super().__init__(world)

        self.waypoints = deque([random.choice(world.get_map().get_spawn_points()).location for _ in range(length)])
