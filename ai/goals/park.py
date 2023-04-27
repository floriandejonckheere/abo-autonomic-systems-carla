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


class Park(Goal):
    """Park the vehicle"""

    def actions(self):
        return [
            # Brake gently
            actions.Brake(self.knowledge.location.distance(self.knowledge.waypoint)),

            # Apply handbrake when stopped
            actions.Handbrake(self.knowledge.speed()),
        ]
