import glob
import os
import sys

try:
    sys.path.append(glob.glob('../../**/*%d.%d-%s.egg' % (
        sys.version_info.major,
        sys.version_info.minor,
        'win-amd64' if os.name == 'nt' else 'linux-x86_64'))[0])
except IndexError:
    pass

import carla

from .scenario import Scenario


class TrafficLights(Scenario):
    """Straight towards the traffic lights, stop if necessary"""

    waypoints = [
        carla.Location(-6.2, 95.6, 1.8431),
        carla.Location(-5.4, 187.0, 1.8431),
        carla.Location(-42.7, 196.9, 1.8431),
    ]

    def __init__(self, world):
        super().__init__(world)

        self.use_spawnpoint = False
