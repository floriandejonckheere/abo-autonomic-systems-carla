import glob
import math
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

from .state_machine import StateMachine


# Class that holds the knowledge of the current state and serves as interaction point for all the modules
class Knowledge(object):
    def __init__(self):
        # Vehicle state
        self.state_machine = StateMachine()

        # Waypoint to navigate towards
        self.waypoint = carla.Location(0.0, 0.0, 0.0)

        # Destination (end of waypoint path)
        self.destination = carla.Location(0.0, 0.0, 0.0)

        # Current location, rotation and velocity of the vehicle
        self.location = carla.Location(0.0, 0.0, 0.0)
        self.rotation = carla.Rotation(0.0, 0.0, 0.0)
        self.velocity = carla.Vector3D(0.0, 0.0, 0.0)

        # Current target speed
        self.target_speed = 0.0

        # Traffic light information
        self.is_at_traffic_light = False
        self.traffic_light = None

        # Sensor data
        self.lane_invasion = False
        self.collision = False
        self.depth_image = None

        # Parsed sensor data
        self.proximity = 0.0

        # Execution plan
        self.plan = None

    def state(self):
        return self.state_machine.current_state

    def speed(self):
        return 3.6 * math.sqrt(self.velocity.x ** 2 + self.velocity.y ** 2 + self.velocity.z ** 2)

    # A function to receive data from monitor
    def update(self, **kwargs):
        self.__dict__.update(kwargs)
