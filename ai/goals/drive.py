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

from .goal import Goal

import ai.actions as actions


class Drive(Goal):
    """Drive towards the next waypoint"""

    def actions(self):
        return [
            # Accelerate towards the next waypoint
            actions.Accelerate(self.knowledge),
            actions.Limit(self.knowledge),

            # Steer towards the next waypoint
            actions.Steer(self.knowledge),
        ]
