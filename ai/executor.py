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

from .controllers.fuzzy import Fuzzy
from .state_machine import StateMachine


# Executor is responsible for moving the vehicle around
# In this implementation it only needs to match the steering and speed so that we arrive at provided waypoints
# BONUS TODO: implement different speed limits so that planner would also provide speed target speed in addition to
#  direction
class Executor(object):
    def __init__(self, knowledge, vehicle):
        self.vehicle = vehicle
        self.knowledge = knowledge

        self.controller = Fuzzy()

    # Update the executor at some intervals to steer the car in desired direction
    def update(self):
        state = self.knowledge.get_state()
        # TODO: this needs to be able to handle
        if state == StateMachine.driving:
            self.update_control()

    # TODO: steer in the direction of destination and throttle or brake depending on how close we are to destination
    # TODO: Take into account that exiting the crash site could also be done in reverse, so there might need to be
    #  additional data passed between planner and executor, or there needs to be some way to tell this that it is ok
    #  to drive in reverse during healing and crashed states. An example is additional_vars, that could be a list with
    #  parameters that can tell us which things we can do (for example going in reverse)
    def update_control(self):
        # Get current and target speed
        speed = self.knowledge.get_speed()
        target_speed = self.knowledge.get_target_speed()

        # Distance and angle to waypoint
        distance = self.knowledge.get_distance_to_waypoint()
        angle = self.knowledge.get_angle_to_waypoint()

        # Update fuzzy controller
        self.controller.update(distance, speed, target_speed, angle)

        control = carla.VehicleControl()

        # Set throttle and brake
        control.throttle = self.controller.get_throttle()
        control.brake = self.controller.get_brake()
        control.hand_brake = False

        # Set steering
        control.steer = self.controller.get_steer()

        # Apply control
        self.vehicle.apply_control(control)
