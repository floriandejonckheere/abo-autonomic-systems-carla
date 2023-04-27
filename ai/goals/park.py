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
            # FIXME: brake softly based on speed
            actions.Handbrake(self.knowledge),
        ]
