import time

import numpy as np

from .zone import Zone

# Depth sensor zones, normalized to a 100x100 grid
DEPTH_ZONES = {
    'front': Zone(height=(60, 80), width=(40, 60), color=(255, 0, 0)),
    'left': Zone(height=(20, 80), width=(0, 20), color=(0, 255, 0)),
    'right': Zone(height=(20, 80), width=(80, 100), color=(0, 255, 0)),
}


# Analyzer is responsible for parsing all the data that the knowledge has received from Monitor and turning it into
# something usable
# TODO: During the update step parse the data inside knowledge into information that could be used by planner to plan
#  the route
class Analyzer(object):
    def __init__(self, knowledge, vehicle, debug):
        self.knowledge = knowledge
        self.vehicle = vehicle
        self.debug = debug

    # Function that is called at time intervals to update ai-state
    def update(self, dt):
        # Detect collision and transition to crashed state
        self.detect_collision()

        # Analyze LIDAR sensor data
        self.analyze_lidar_image()

        # Analyze proximity sensor data
        self.analyze_proximity_data()

        # Avoid collisions and transition to healing state
        self.avoid_collision()

    def detect_collision(self):
        if self.knowledge.collision and not self.knowledge.state_machine.crashed.is_active:
            self.knowledge.state_machine.crash()

    def analyze_lidar_image(self):
        pass

    def analyze_proximity_data(self):
        # Proximity to obstacle in front (cruise control)
        self.knowledge.proximity = DEPTH_ZONES['front'].analyze(self.convert_proximity_image(self.knowledge.proximity_image))
        self.knowledge.obstacle = self.knowledge.proximity < 20

        # Proximity to obstacle on left and right (collision avoidance)
        self.knowledge.proximity_left = np.mean(self.convert_proximity_image(self.knowledge.proximity_image_left))
        self.knowledge.obstacle_left = self.knowledge.proximity_left < 20

        self.knowledge.proximity_right = np.mean(self.convert_proximity_image(self.knowledge.proximity_image_right))
        self.knowledge.obstacle_right = self.knowledge.proximity_right < 20

    def convert_proximity_image(self, image):
        array = np.frombuffer(image.raw_data, dtype=np.dtype("uint8"))
        array = np.reshape(array, (image.height, image.width, 4))
        array = array[:, :, :3]
        array = array[:, :, ::-1]

        return array

    def avoid_collision(self):
        if self.knowledge.state_machine.healing.is_active:
            last_event, timestamp = self.knowledge.state_machine.history[-1]

            # Go back to driving if healing timeout has passed
            if time.time() - timestamp > 5.0:
                self.knowledge.state_machine.drive()
        else:
            # Avoid collision if proximity is too low
            if self.knowledge.obstacle or self.knowledge.obstacle_left or self.knowledge.obstacle_right:
                self.knowledge.state_machine.heal()
