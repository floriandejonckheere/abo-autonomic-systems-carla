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

import ai.utils as utils

from .state_machine import StateMachine
from .navigator import Navigator


# Planner is responsible for creating a plan for moving around
# In our case it creates a list of waypoints to follow so that vehicle arrives at destination
# Alternatively this can also provide a list of waypoints to try avoid crashing or 'uncrash' itself
class Planner(object):
    def __init__(self, knowledge, vehicle):
        self.knowledge = knowledge

        self.navigator = Navigator(knowledge, vehicle.get_world())

    # Function that is called at time intervals to update ai-state
    def update(self):
        state = self.knowledge.state()

        # TODO: Take into account traffic lights and other cars
        # TODO: Implement crash handling. Probably needs to be done by following waypoint list to exit the crash site.
        # Afterwards needs to remake the path.
        # TODO: implement function for crash handling, should provide map of waypoints to move towards to for exiting
        #  crash state. You should use separate waypoint list for that, to not mess with the original path.

        if state == StateMachine.parked:
            # If the vehicle is parked, apply handbrake
            return
        elif state == StateMachine.arrived or state == StateMachine.idle:
            # Check for a new destination and plan the path
            if self.knowledge.destination is not None and utils.distance(self.knowledge.location, self.knowledge.destination) > 5.0:
                self.navigator.plan()

            # Drive to new waypoint
            # FIXME: vehicle will end up in an infinite loop if the destination is not changed from outside
            self.drive()
        elif state == StateMachine.driving:
            self.drive()

    def drive(self):
        # Update plan based on current knowledge
        waypoint = self.navigator.update()

        if waypoint is None:
            # If there are no more waypoints, we have arrived
            self.knowledge.state_machine.arrive()
        else:
            # Otherwise, we keep driving to the next waypoint
            self.knowledge.update(waypoint=waypoint)

            self.knowledge.state_machine.drive()

