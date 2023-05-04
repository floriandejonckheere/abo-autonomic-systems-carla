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

import numpy as np

# Depth sensor zones, normalized to a 100x100 grid
ZONES = {
    'cruise': {
        'height': (50, 70),
        'width': (65, 95),
        'color': [255, 0, 0],
    },
}


# Analyzer is responsible for parsing all the data that the knowledge has received from Monitor and turning it into
# something usable
# TODO: During the update step parse the data inside knowledge into information that could be used by planner to plan
#  the route
class Analyzer(object):
    def __init__(self, knowledge):
        self.knowledge = knowledge

    # Function that is called at time intervals to update ai-state
    def update(self):
        # Detect collision and transition to crashed state
        self.detect_collision()

        # Analyze depth sensor data
        self.analyze_depth_image()

    def detect_collision(self):
        if self.knowledge.collision:
            self.knowledge.state_machine.crash()

    def analyze_depth_image(self):
        # Convert to logarithmic grayscale
        self.knowledge.depth_image.convert(carla.ColorConverter.LogarithmicDepth)

        array = np.frombuffer(self.knowledge.depth_image.raw_data, dtype=np.dtype("uint8"))
        array = np.reshape(array, (self.knowledge.depth_image.height, self.knowledge.depth_image.width, 4))
        array = array[:, :, :3]
        array = array[:, :, ::-1]

        # Analyze depth sensor zones
        self.knowledge.proximity = np.mean(array[ZONES['cruise']['height'][0]:ZONES['cruise']['height'][1]])

        # Proximity to obstacle in front
        # self.knowledge.proximity = np.mean(array)
