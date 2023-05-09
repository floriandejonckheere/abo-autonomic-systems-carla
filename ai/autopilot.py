import time

from .monitor import *
from .analyzer import *
from .planner import *
from .executor import *
from .knowledge import *


# Manager script
class Autopilot(object):
    def __init__(self, vehicle, debug):
        # Vehicle (CARLA actor)
        self.vehicle = vehicle
        self.debug = debug

        # MAPE-K modules
        self.knowledge = Knowledge()
        self.monitor = Monitor(self.knowledge, self.vehicle, debug)
        self.analyzer = Analyzer(self.knowledge, self.vehicle, debug)
        self.planner = Planner(self.knowledge, self.vehicle, debug)
        self.executor = Executor(self.knowledge, self.vehicle, debug)

        # Time of last update (in milliseconds)
        self.last_time = int(round(time.time() * 1000))

    # Update all the modules and return the current status
    def update(self):
        # Calculate delta time since last update (in milliseconds)
        ctime = int(round(time.time() * 1000))
        dt = ctime - self.last_time
        self.last_time = ctime

        self.monitor.update(dt)
        self.analyzer.update(dt)
        self.planner.update(dt)
        self.executor.update(dt)

        return self.knowledge.state_machine.current_state

    def destroy(self):
        self.monitor.destroy()

    # Main interaction point with autopilot - set the destination, so that it does the rest
    def set_destination(self, destination: carla.Location):
        # Set destination in knowledge, so that planner can plan the route
        self.knowledge.update(destination=destination)
