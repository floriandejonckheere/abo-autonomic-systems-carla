import numpy as np

from .zone import Zone

# Depth sensor zones, normalized to a 100x100 grid
DEPTH_ZONES = {
    'front': Zone(height=(40, 60), width=(40, 60), color=(255, 0, 0)),
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

    def detect_collision(self):
        if self.knowledge.collision and not self.knowledge.state_machine.crashed.is_active:
            self.knowledge.state_machine.crash()

    def analyze_lidar_image(self):
        pass

    def analyze_proximity_data(self):
        array = np.frombuffer(self.knowledge.proximity_image.raw_data, dtype=np.dtype("uint8"))
        array = np.reshape(array, (self.knowledge.proximity_image.height, self.knowledge.proximity_image.width, 4))
        array = array[:, :, :3]
        array = array[:, :, ::-1]

        # Proximity to obstacle in front (cruise control)
        self.knowledge.proximity = DEPTH_ZONES['front'].analyze(array)

        # Proximity to obstacle on left (collision avoidance)
        self.knowledge.proximity_left = DEPTH_ZONES['left'].analyze(array)
        self.knowledge.proximity_right = DEPTH_ZONES['right'].analyze(array)

        self.knowledge.proximity = np.mean(array)
