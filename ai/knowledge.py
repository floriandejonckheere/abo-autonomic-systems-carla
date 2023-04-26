import glob
import os
import sys
import math

try:
    sys.path.append(glob.glob('../**/*%d.%d-%s.egg' % (
        sys.version_info.major,
        sys.version_info.minor,
        'win-amd64' if os.name == 'nt' else 'linux-x86_64'))[0])
except IndexError:
    pass

import carla

import ai.utils as utils

from .events.broker import broker
from .state_machine import StateMachine


# Class that holds the knowledge of the current state and serves as interaction point for all the modules
class Knowledge(object):
    def __init__(self):
        # Vehicle state
        self.state_machine = StateMachine()

        # Waypoint to navigate towards
        self.waypoint = carla.Location(0.0, 0.0, 0.0)

        # Final destination
        self.destination = carla.Location(0.0, 0.0, 0.0)

        # Current location, rotation and velocity of the vehicle
        self.location = carla.Location(0.0, 0.0, 0.0)
        self.rotation = carla.Rotation(0.0, 0.0, 0.0)
        self.velocity = carla.Vector3D(0.0, 0.0, 0.0)

        # Current target speed
        self.target_speed = 0.0

        # Lane invasion
        self.lane_invasion = False

    def state(self):
        return self.state_machine.current_state

    def speed(self):
        return 3.6 * math.sqrt(self.velocity.x ** 2 + self.velocity.y ** 2 + self.velocity.z ** 2)

    def distance_to_waypoint(self):
        return utils.distance(self.location, self.waypoint)

    def angle_to_waypoint(self):
        # Source vector
        source = self.rotation.get_forward_vector()
        source_vector = [source.x, source.y]

        # Destination vector (relative to current position of vehicle)
        target_vector = [self.waypoint.x - self.location.x, self.waypoint.y - self.location.y]

        return utils.angle(source_vector, target_vector)

    # A function to receive data from monitor
    def update(self, **kwargs):
        self.__dict__.update(kwargs)

        broker.publish('data_changed', **kwargs)
