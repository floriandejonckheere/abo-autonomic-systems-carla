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
        source = self.vehicle.get_transform().get_forward_vector()

        # Get current and target speed
        speed = self.knowledge.get_speed()
        target_speed = self.knowledge.get_target_speed()

        # Distance to waypoint
        distance = utils.distance(self.vehicle.get_location(), destination)

        # print(f'x={source.x}, y={source.y}, x={self.vehicle.get_transform().get_forward_vector().x}, y={self.vehicle.get_transform().get_forward_vector().y}')

        # Normalize source and destination vectors
        source_norm = [source.x, source.y]
        source_norm /= np.linalg.norm(source_norm)

        destination_norm = [destination.x, destination.y]
        destination_norm /= np.linalg.norm(destination_norm)

        # Calculate dot product between vectors
        dot_product = np.dot(source_norm, destination_norm)

        # Calculate cross product between vectors
        cross_product = np.cross(source_norm, destination_norm)

        # Calculate angle in radians
        angle_radians = np.arccos(dot_product)

        # Determine direction of angle using cross product
        if cross_product < 0:
            angle_radians = -angle_radians

        # Convert angle from radians to degrees
        angle_degrees = np.degrees(angle_radians)

        # steer = angle_degrees - 180.0
        if cross_product < 0:
            steer = 0.3
        else:
            steer = -0.3

        print(f'cp={cross_product:.2f}, angle={angle_degrees:.2f}, steering={steer:.2f}')

        # Update fuzzy controller
        self.controller.update(distance, speed, target_speed)

        control = carla.VehicleControl()

        # Apply throttle and brake
        control.throttle = self.controller.get_throttle()
        control.brake = self.controller.get_brake()

        # Debug lines
        self.vehicle.get_world().debug.draw_line(source, destination, life_time=0.5, color=carla.Color(255, 255, 255))
        self.vehicle.get_world().debug.draw_line(source, source + carla.Location(5, 0, 0), life_time=0.5, color=carla.Color(255, 0, 0))
        self.vehicle.get_world().debug.draw_line(source, source + carla.Location(0, 5, 0), life_time=0.5, color=carla.Color(0, 255, 0))
        self.vehicle.get_world().debug.draw_line(source, source + carla.Location(0, 0, 5), life_time=0.5, color=carla.Color(0, 0, 255))

        control.steer = min(0.3, max(-0.3, steer))
        control.hand_brake = False

        self.vehicle.apply_control(control)
