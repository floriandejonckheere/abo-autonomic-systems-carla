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
        distance = self.knowledge.distance(self.vehicle.get_location(), destination)

        print(f'[{self.knowledge.get_status()}] location: {self.vehicle.get_location()}, destination: {destination}, distance: {distance}')

        # Calculate throttle and heading
        control = carla.VehicleControl()

        # Apply throttle if vehicle is far away from destination
        if distance > 10.0:
            control.throttle = 0.6
            control.brake = 0.0
        else:
            control.throttle = 0.0
            control.brake = 1.0

        control.steer = 0.0
        control.hand_brake = False

        print(f'Control: throttle={control.throttle}, steer={control.steer}, brake={control.brake}, hand_brake={control.hand_brake}')

        self.vehicle.apply_control(control)
