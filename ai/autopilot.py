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

import time

from .monitor import *
from .analyzer import *
from .planner import *
from .executor import *
from .knowledge import *


# Manager script
class Autopilot(object):
    def __init__(self, vehicle):
        self.vehicle = vehicle
        self.knowledge = Knowledge()
        self.knowledge.set_status_changed_callback(self.status_updated)
        self.analyzer = Analyzer(self.knowledge)
        self.monitor = Monitor(self.knowledge, self.vehicle)
        self.planner = Planner(self.knowledge, self.vehicle)
        self.executor = Executor(self.knowledge, self.vehicle)
        self.prev_time = int(round(time.time() * 1000))
        self.route_finished = lambda *_, **__: None
        self.crashed = lambda *_, **__: None

    def status_updated(self, new_status):
        if new_status == Status.ARRIVED:
            self.route_finished()
        if new_status == Status.CRASHED:
            self.crashed(self)

    def set_route_finished_callback(self, callback):
        self.route_finished = callback

    def set_crash_callback(self, callback):
        self.crashed = callback

    def get_vehicle(self):
        return self.vehicle

    # Update all the modules and return the current status
    def update(self):
        ctime = int(round(time.time() * 1000))
        delta_time = ctime - self.prev_time
        self.prev_time = ctime

        self.monitor.update(delta_time)
        self.analyzer.update(delta_time)
        self.planner.update(delta_time)
        self.executor.update(delta_time)

        return self.knowledge.get_status()

    # Main interaction point with autopilot - set the destination, so that it does the rest
    def set_destination(self, destination):
        self.planner.make_plan(self.vehicle.get_transform(), destination)
