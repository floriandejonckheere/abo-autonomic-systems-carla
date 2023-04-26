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

from .state_machine import StateMachine


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
    def update(self):
        self.update_plan()
        self.knowledge.update_destination(self.get_current_destination())

    # Update internal state to make sure that there are waypoints to follow and that we have not arrived yet
    def update_plan(self):
        # If the car is parked, we are not going anywhere
        if self.knowledge.get_state() == StateMachine.parked:
            return

        # If we have no waypoints, then we have arrived
        if len(self.path) == 0:
            self.knowledge.state_machine.arrive()
            return

        # If we are close enough to the next waypoint, remove it from the list
        if utils.distance(self.knowledge.get_location(), self.path[0]) < 5.0:
            self.path.popleft()

        if len(self.path) == 0:
            # If we have no waypoints, then we have arrived
            self.knowledge.state_machine.arrive()
        else:
            # Otherwise, we keep driving (possibly after arriving)
            self.knowledge.state_machine.drive()

    # Get current destination
    def get_current_destination(self):
        state = self.knowledge.get_state()

        # If we are driving, then the current destination is next waypoint
        if state == StateMachine.driving:
            # TODO: Take into account traffic lights and other cars
            return self.path[0]
        if state == StateMachine.arrived:
            return self.knowledge.get_location()
        if state == StateMachine.healing:
            # TODO: Implement crash handling. Probably needs to be done by following waypoint list to exit the crash site.
            # Afterwards needs to remake the path.
            return self.knowledge.get_location()
        if state == StateMachine.crashed:
            # TODO: implement function for crash handling, should provide map of waypoints to move towards to for exiting
            #  crash state. You should use separate waypoint list for that, to not mess with the original path.
            return self.knowledge.get_location()
        # Otherwise destination is same as current position
        return self.knowledge.get_location()

    def build_path(self, source, destination):
        path = deque([])

        debug = self.vehicle.get_world().debug

        # Current waypoint
        waypoint = self.knowledge.get_waypoint()

        distance = float('inf')

        # Iterate over waypoints until we are close enough to the destination,
        # or the distance is increasing again (the vehicle overshot)
        while distance > 5.0 and len(path) < 150: # and utils.distance(waypoint.transform.location, destination) < distance:
            # Compute current waypoint distance to destination
            distance = utils.distance(waypoint.transform.location, destination)

            # Draw current waypoint
            debug.draw_point(waypoint.transform.location, size=0.2, life_time=20)
            # print(f'Waypoint: ({waypoint.transform.location.x}, {waypoint.transform.location.y}) i={waypoint.is_intersection} lc={waypoint.lane_change} lt={waypoint.lane_type} d={distance}')

            # Get next (legal) waypoints
            next_waypoints = waypoint.next(2.0)

            # If there is only one next waypoint, then select it
            if len(next_waypoints) == 1:
                waypoint = next_waypoints[0]
            else:
                for wp in next_waypoints:
                    debug.draw_point(wp.transform.location, size=0.1, life_time=20, color=carla.Color(0, 255, 0))

                # If there are multiple next waypoints, then select the one that is closest to destination
                waypoint = min(next_waypoints, key=lambda wp: utils.distance(wp.transform.location, destination))

            # Add waypoint to path
            path.append(waypoint.transform.location)

        # Add destination to path
        path.append(destination)

        return path
