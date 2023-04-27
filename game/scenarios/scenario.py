import glob
import os
import sys

try:
    sys.path.append(glob.glob('../../**/*%d.%d-%s.egg' % (
        sys.version_info.major,
        sys.version_info.minor,
        'win-amd64' if os.name == 'nt' else 'linux-x86_64'))[0])
except IndexError:
    pass

import carla


class Scenario:
    waypoints = []

    def __init__(self, world):
        self.world = world
        self.actors = []

    def setup(self):
        pass

    def teardown(self):
        for actor in self.actors:
            actor.is_alive and actor.destroy()
