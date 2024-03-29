from collections import deque

from ai.carla import carla

from .state.state_machine import StateMachine
from .state.value import Value


class Knowledge(object):
    """Knowledge is responsible for storing the current state of the vehicle."""

    def __init__(self):
        # Vehicle state
        self.state_machine = StateMachine()

        # Waypoint to navigate towards
        self.waypoint = carla.Location(0.0, 0.0, 0.0)

        # Destination (end of waypoint path)
        self.destination = carla.Location(0.0, 0.0, 0.0)

        # Distance to destination (using waypoint path)
        self.distance = 0.0

        # Current location, rotation and velocity of the vehicle
        self.location = carla.Location(0.0, 0.0, 0.0)
        self.rotation = carla.Rotation(0.0, 0.0, 0.0)
        self.velocity = carla.Vector3D(0.0, 0.0, 0.0)

        # Calculated speed
        self.speed = 0.0

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

        self.depth_image = None

        # Proximity to obstacle in front
        self.proximity = 0.0

        # Proximity to obstacle left and right (moving average)
        self.proximity_left = Value(value=float('inf'), size=5)
        self.proximity_right = Value(value=float('inf'), size=5)

        # Obstacle detected
        self.obstacle = False
        self.obstacle_left = False
        self.obstacle_right = False

        # Execution plan
        self.plan = None

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
