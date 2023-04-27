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


class Stop(Goal):
    """Stop at traffic lights"""

    def actions(self):
        # Don't stop if there is no traffic light or if the traffic light is green
        if not self.knowledge.is_at_traffic_light or self.knowledge.traffic_light.state == carla.TrafficLightState.Green:
            return []

        return [
            actions.Brake(self.knowledge.location, self.knowledge.waypoint),
        ]
