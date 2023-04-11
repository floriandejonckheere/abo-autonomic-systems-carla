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
from .knowledge import Status


# Executor is responsible for moving the vehicle around
# In this implementation it only needs to match the steering and speed so that we arrive at provided waypoints
# BONUS TODO: implement different speed limits so that planner would also provide speed target speed in addition to
#  direction
class Executor(object):
    def __init__(self, knowledge, vehicle):
        self.vehicle = vehicle
        self.knowledge = knowledge
        self.target_pos = knowledge.get_location()
        self.controller = Fuzzy()

    # Update the executor at some intervals to steer the car in desired direction
    def update(self, time_elapsed):
        status = self.knowledge.get_status()
        # TODO: this needs to be able to handle
        if status == Status.DRIVING:
            dest = self.knowledge.get_current_destination()
            self.update_control(dest, [1], time_elapsed)

    # TODO: steer in the direction of destination and throttle or brake depending on how close we are to destination
    # TODO: Take into account that exiting the crash site could also be done in reverse, so there might need to be
    #  additional data passed between planner and executor, or there needs to be some way to tell this that it is ok
    #  to drive in reverse during HEALING and CRASHED states. An example is additional_vars, that could be a list with
    #  parameters that can tell us which things we can do (for example going in reverse)
    def update_control(self, destination, additional_vars, delta_time):
        # Calculate Euclidian distance to destination
        distance = self.knowledge.distance(self.vehicle.get_location(), destination)

        # Update fuzzy controller
        self.controller.update(distance)

        control = carla.VehicleControl()

        # Calculate throttle and brake
        control.throttle = self.controller.get_throttle()
        control.brake = self.controller.get_brake()

        # Calculate steering
        control.steer = 0.0
        control.hand_brake = False

        # print(f's={self.knowledge.get_status()} v={self.knowledge.get_speed():.2f} d={distance:.2f}, t={control.throttle:.2f} s={control.steer:.2f} b={control.brake:.2f} hb={control.hand_brake:.2f}')
        print(f'v={self.knowledge.get_speed():.2f} vt={self.knowledge.get_target_speed():.2f}')

        self.vehicle.apply_control(control)
