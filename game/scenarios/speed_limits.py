from ai.carla import carla

import threading
import time

from .scenario import Scenario

import game.utils as utils


class SpeedLimits(Scenario):
    """Straight raod with changing speed limits"""

    waypoints = [
        carla.Location(148.5, 193.1, 1.8431),
        carla.Location(12.7, 193.3, 1.8431),
    ]

    def __init__(self, world):
        super().__init__(world)

        self.use_spawnpoint = False
