import glob
import os
import sys
import math

import numpy as np

try:
    sys.path.append(glob.glob('../**/*%d.%d-%s.egg' % (
        sys.version_info.major,
        sys.version_info.minor,
        'win-amd64' if os.name == 'nt' else 'linux-x86_64'))[0])
except IndexError:
    pass

from enum import Enum

import carla

import ai.utils as utils

from .state_machine import StateMachine


# Class that holds the knowledge of the current state and serves as interaction point for all the modules
class Knowledge(object):
    def __init__(self):
        # Vehicle state
        self.state_machine = StateMachine()

        # Waypoint to navigate towards
        self.waypoint = carla.Location(0.0, 0.0, 0.0)

        # Current location, rotation and velocity of the vehicle
        self.location = carla.Location(0.0, 0.0, 0.0)
        self.rotation = carla.Rotation(0.0, 0.0, 0.0)
        self.velocity = carla.Vector3D(0.0, 0.0, 0.0)

        # Current target speed
        self.target_speed = 0.0

        # Lane invasion
        self.lane_invasion = False

        # Callbacks
        self.state_changed = lambda *_, **__: None
        self.destination_changed = lambda *_, **__: None
        self.data_changed = lambda *_, **__: None

    def get_state(self):
        return self.state_machine.current_state

    def get_waypoint(self):
        return self.waypoint

    def get_location(self):
        return self.location

    def get_rotation(self):
        return self.rotation

    def get_velocity(self):
        return self.velocity

    def get_target_speed(self):
        return self.target_speed

    def get_speed(self):
        return 3.6 * math.sqrt(self.velocity.x ** 2 + self.velocity.y ** 2 + self.velocity.z ** 2)

    def get_distance_to_waypoint(self):
        return utils.distance(self.get_location(), self.waypoint)

    def get_angle_to_waypoint(self):
        # Normalize source and destination vectors
        source_vector = self.rotation.get_forward_vector()
        source_norm = [source_vector.x, source_vector.y]
        source_norm /= np.linalg.norm(source_norm)

        # Destination vector (relative to current position of vehicle)
        waypoint_norm = [self.waypoint.x - self.location.x, self.waypoint.y - self.location.y]
        waypoint_norm /= np.linalg.norm(waypoint_norm)

        # Calculate dot product between vectors
        dot_product = np.dot(source_norm, waypoint_norm)

        # Calculate cross product between vectors
        cross_product = np.cross(source_norm, waypoint_norm)

        # Calculate angle in radians
        angle_radians = np.arccos(dot_product)

        # Determine direction of angle using cross product
        if cross_product < 0:
            angle_radians = -angle_radians

        # Convert angle from radians to degrees
        return np.degrees(angle_radians)

    # Whether the vehicle has arrived at the destination
    def arrived_at(self, destination):
        return utils.distance(self.get_location(), destination) < 5.0

    def update_destination(self, new_destination):
        if utils.distance(self.waypoint, new_destination) > 5.0:
            self.waypoint = new_destination
            self.destination_changed(new_destination)

    # A function to receive data from monitor
    # TODO: Add callback so that analyzer can know when to parse the data
    def update(self, **kwargs):
        self.__dict__.update(kwargs)

        for key in kwargs:
            self.data_changed(key)

    def set_destination_changed_callback(self, callback):
        self.destination_changed = callback

    def set_data_changed_callback(self, callback):
        self.data_changed = callback
