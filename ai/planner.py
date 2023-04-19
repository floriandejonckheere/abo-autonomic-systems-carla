import glob
import os
import sys
from collections import deque

try:
    sys.path.append(glob.glob('../**/*%d.%d-%s.egg' % (
        sys.version_info.major,
        sys.version_info.minor,
        'win-amd64' if os.name == 'nt' else 'linux-x86_64'))[0])
except IndexError:
    pass

import carla

import ai.utils as utils

from .knowledge import Status


# Planner is responsible for creating a plan for moving around
# In our case it creates a list of waypoints to follow so that vehicle arrives at destination
# Alternatively this can also provide a list of waypoints to try avoid crashing or 'uncrash' itself
class Planner(object):
    def __init__(self, knowledge, vehicle):
        self.knowledge = knowledge
        self.vehicle = vehicle

        # List of waypoints to follow
        self.path = deque([])

    # Create a map of waypoints to follow to the destination and save it
    def make_plan(self, source, destination):
        self.path = self.build_path(source, destination)
        self.update_plan()
        self.knowledge.update_destination(self.get_current_destination())

    # Function that is called at time intervals to update ai-state
    def update(self, time_elapsed):
        self.update_plan()
        self.knowledge.update_destination(self.get_current_destination())

    # Update internal state to make sure that there are waypoints to follow and that we have not arrived yet
    def update_plan(self):
        if len(self.path) == 0:
            return

        if self.knowledge.arrived_at(self.path[0]):
            self.path.popleft()

        if len(self.path) == 0:
            self.knowledge.update_status(Status.ARRIVED)
        else:
            self.knowledge.update_status(Status.DRIVING)

    # Get current destination
    def get_current_destination(self):
        status = self.knowledge.get_status()
        # If we are driving, then the current destination is next waypoint
        if status == Status.DRIVING:
            # TODO: Take into account traffic lights and other cars
            return self.path[0]
        if status == Status.ARRIVED:
            return self.knowledge.get_location()
        if status == Status.HEALING:
            # TODO: Implement crash handling. Probably needs to be done by following waypoint list to exit the crash site.
            # Afterwards needs to remake the path.
            return self.knowledge.get_location()
        if status == Status.CRASHED:
            # TODO: implement function for crash handling, should provide map of wayoints to move towards to for exiting
            #  crash state. You should use separate waypoint list for that, to not mess with the original path.
            return self.knowledge.get_location()
        # Otherwise destination is same as current position
        return self.knowledge.get_location()

    # TODO: Implementation
    def build_path(self, source, destination):
        self.path = deque([])
        # TODO: create path of waypoints from source to

        debug = self.vehicle.get_world().debug

        # Current waypoint
        waypoint = self.knowledge.get_waypoint()

        while True:
            # Compute current waypoint distance to destination
            distance = utils.distance(waypoint.transform.location, destination)

            # If we are close enough to destination, then stop
            if distance < 5.0:
                print('Reached destination')
                break

            # Draw current waypoint
            debug.draw_point(waypoint.transform.location, size=0.2, life_time=10)
            print(f'Waypoint: ({waypoint.transform.location.x}, {waypoint.transform.location.y}) i={waypoint.is_intersection} lc={waypoint.lane_change} lt={waypoint.lane_type} d={distance}')

            # Decide on next waypoint
            next_waypoints = waypoint.next(2.0)

            # If there is only one next waypoint, then select it
            if len(next_waypoints) == 1:
                waypoint = next_waypoints[0]
                continue

            # If there are multiple next waypoints, then select the one that is closest to destination
            waypoint = min(next_waypoints, key=lambda wp: utils.distance(wp.transform.location, destination))

            # Add waypoint to path
            self.path.append(waypoint.transform.location)

            # If the distance is increasing (the vehicle overshot), then stop
            if utils.distance(waypoint.transform.location, destination) > distance:
                print('Overshot destination')
                break

        # Add destination to path
        self.path.append(destination)

        return self.path
