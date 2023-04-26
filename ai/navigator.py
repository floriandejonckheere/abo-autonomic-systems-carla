import glob
import os
import sys

try:
    sys.path.append(glob.glob('../**/*%d.%d-%s.egg' % (
        sys.version_info.major,
        sys.version_info.minor,
        'win-amd64' if os.name == 'nt' else 'linux-x86_64'))[0])
except IndexError:
    pass

import carla

from collections import deque

import ai.utils as utils


class Navigator:
    def __init__(self, world: carla.World):
        self.world = world
        self.map = world.get_map()

    def navigate(self, source: carla.Location, destination: carla.Location) -> deque:
        path = deque([])

        # Waypoint on map closest to source location
        waypoint = self.map.get_waypoint(source)

        distance = float('inf')

        # Iterate over waypoints until we are close enough to the destination,
        # or the distance is increasing again (the vehicle overshot)
        while distance > 5.0 and len(path) < 150: # and utils.distance(waypoint.transform.location, destination) < distance:
            # Compute current waypoint distance to destination
            distance = utils.distance(waypoint.transform.location, destination)

            # Draw current waypoint
            self.world.debug.draw_point(waypoint.transform.location, size=0.2, life_time=20)
            # print(f'Waypoint: ({waypoint.transform.location.x}, {waypoint.transform.location.y}) i={waypoint.is_intersection} lc={waypoint.lane_change} lt={waypoint.lane_type} d={distance}')

            # Get next (legal) waypoints
            next_waypoints = waypoint.next(2.0)

            # If there is only one next waypoint, then select it
            if len(next_waypoints) == 1:
                waypoint = next_waypoints[0]
            else:
                for wp in next_waypoints:
                    self.world.debug.draw_point(wp.transform.location, size=0.1, life_time=20, color=carla.Color(0, 255, 0))

                # If there are multiple next waypoints, then select the one that is closest to destination
                waypoint = min(next_waypoints, key=lambda wp: utils.distance(wp.transform.location, destination))

            # Add waypoint to path
            path.append(waypoint.transform.location)

        # Add destination to path
        path.append(destination)

        return path
