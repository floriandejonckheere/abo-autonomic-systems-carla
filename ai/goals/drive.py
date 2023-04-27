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
        # Target location vector (relative to source)
        target = carla.Location(
            self.knowledge.waypoint.x - self.knowledge.location.x,
            self.knowledge.waypoint.y - self.knowledge.location.y,
        )

        return [
            # Accelerate towards a waypoint
            actions.Accelerate(self.knowledge.location, self.knowledge.waypoint),
            actions.Limit(self.knowledge.speed(), self.knowledge.target_speed),

            # Steer towards the next waypoint
            actions.Steer(self.knowledge.rotation.get_forward_vector(), target),
        ]
