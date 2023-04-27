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


class MilestoneTwo(Scenario):
    """Drive to the gas station"""

    waypoints = [
        carla.Location(42.5959, -4.3443, 1.8431),
        carla.Location(-30, 167, 1.8431),
    ]
