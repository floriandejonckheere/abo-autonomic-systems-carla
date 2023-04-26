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

from .monitor import *
from .analyzer import *
from .planner import *
from .executor import *
from .knowledge import *


# Manager script
class Autopilot(object):
    def __init__(self, vehicle):
        # Vehicle (CARLA actor)
        self.vehicle = vehicle

        # MAPE-K modules
        self.knowledge = Knowledge()
        self.monitor = Monitor(self.knowledge, self.vehicle)
        self.analyzer = Analyzer(self.knowledge)
        self.planner = Planner(self.knowledge, self.vehicle)
        self.executor = Executor(self.knowledge, self.vehicle)

    # Update all the modules and return the current status
    def update(self):
        self.monitor.update()
        self.analyzer.update()
        self.planner.update()
        self.executor.update()

        return self.knowledge.state()

    # Main interaction point with autopilot - set the destination, so that it does the rest
    def set_destination(self, destination: carla.Location):
        # Set destination in knowledge
        self.knowledge.update(destination=destination)

        # Clear the current plan and replan
        self.planner.replan()
