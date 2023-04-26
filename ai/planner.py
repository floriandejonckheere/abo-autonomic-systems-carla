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
from .navigator import Navigator


# Planner is responsible for creating a plan for moving around
# In our case it creates a list of waypoints to follow so that vehicle arrives at destination
# Alternatively this can also provide a list of waypoints to try avoid crashing or 'uncrash' itself
class Planner(object):
    def __init__(self, knowledge, vehicle):
        self.knowledge = knowledge
        self.vehicle = vehicle

        self.navigator = Navigator(self.vehicle.get_world())

        # List of waypoints to follow
        self.path = deque([])

    # Create a map of waypoints to follow to the destination and save it
    def replan(self):
        # Create a new path from the current location to the current destination
        self.path = self.navigator.navigate(self.knowledge.get_location(), self.knowledge.get_destination())

        # Modify plan based on current knowledge
        self.update_plan()

        # Set next waypoint
        self.knowledge.update(waypoint=self.get_current_destination())

    # Function that is called at time intervals to update ai-state
    def update(self):
        # Modify plan based on current knowledge
        self.update_plan()

        # Set next waypoint
        self.knowledge.update(waypoint=self.get_current_destination())

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
