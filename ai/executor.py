import glob
import os
import sys

import numpy as np

try:
    sys.path.append(glob.glob('../**/*%d.%d-%s.egg' % (
        sys.version_info.major,
        sys.version_info.minor,
        'win-amd64' if os.name == 'nt' else 'linux-x86_64'))[0])
except IndexError:
    pass

import carla

import ai.utils as utils

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
        # Get (current) location
        source = self.knowledge.get_location()

        # Get current and target speed
        speed = self.knowledge.get_speed()
        target_speed = self.knowledge.get_target_speed()

        # Distance to waypoint
        distance = utils.distance(self.vehicle.get_location(), destination)

        # Angle between vehicle and waypoint
        angle = utils.angle([source.x, source.y], [destination.x, destination.y])

        # Current rotation of the vehicle (in radians, shifted with 2*PI)
        rotation = np.deg2rad(self.knowledge.get_rotation().yaw + 180)

        # print(f's={self.knowledge.get_status()} v={self.knowledge.get_speed():.2f} d={distance:.2f}, t={control.throttle:.2f} s={control.steer:.2f} b={control.brake:.2f} hb={control.hand_brake:.2f}')
        # print(f'v={speed:.2f} vt={target_speed:.2f}')
        print(f's=({source.x:.2f}, {source.y:.2f}) d=({destination.x:.2f}, {destination.y:.2f}) r=({rotation:.2f}) a={angle:.2f} d={distance:.2f}')

        # Update fuzzy controller
        self.controller.update(distance, speed, target_speed)

        control = carla.VehicleControl()

        # Apply throttle and brake
        control.throttle = self.controller.get_throttle()
        control.brake = self.controller.get_brake()

        # Apply steering
        self.vehicle.get_world().debug.draw_line(source, destination, life_time=0.5, color=carla.Color(255, 0, 0))
        control.steer = min(0.7, max(-0.7, (angle - rotation) / 2))
        control.hand_brake = False

        self.vehicle.apply_control(control)
