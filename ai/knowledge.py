import math

from collections import deque

from ai.carla import carla

from .state_machine import StateMachine
from .value import Value


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

        # Location history (used for crash recovery)
        self.location_history = deque(maxlen=3)
        self.last_location_at = None

        # Current target speed
        self.target_speed = 0.0

        # Traffic light information
        self.is_at_traffic_light = False
        self.traffic_light = None

        # Sensor data
        self.lane_invasion = []
        self.collision = False
        self.lidar_image = None
        self.rgb_image = None

        self.proximity_image = None
        self.proximity_image_left = None
        self.proximity_image_right = None

        # Parsed sensor data
        self.proximity = 0.0
        self.proximity_left = 0.0
        self.proximity_right = 0.0

        self.obstacles = []
        self.obstacles_left = []
        self.obstacles_right = []

        self.obstacle = False
        self.obstacle_left = False
        self.obstacle_right = False

        # Execution plan
        self.plan = None

    def speed(self):
        return 3.6 * math.sqrt(self.velocity.x ** 2 + self.velocity.y ** 2 + self.velocity.z ** 2)

    # A function to receive data from monitor
    def update(self, **kwargs):
        for key, value in kwargs.items():
            if hasattr(self, key):
                if isinstance(getattr(self, key), Value):
                    # Update historic values
                    getattr(self, key).update(value)
                else:
                    # Update simple values
                    setattr(self, key, value)
