import time

from ai.carla import carla

from .monitor import Monitor
from .analyzer import Analyzer
from .planner import Planner
from .executor import Executor
from .knowledge import Knowledge


class Autopilot(object):
    """Autopilot is responsible for managing all the modules and updating them at appropriate intervals."""

    def __init__(self, vehicle, debug, profile):
        # Vehicle (CARLA actor)
        self.vehicle = vehicle
        self.debug = debug
        self.profile = profile

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

        if self.profile:
            # Update all modules and measure elapsed time
            mtime = self.measure(lambda: self.monitor.update(dt))
            atime = self.measure(lambda: self.analyzer.update(dt))
            ptime = self.measure(lambda: self.planner.update(dt))
            etime = self.measure(lambda: self.executor.update(dt))

            print(f'Monitor: {mtime}ms, Analyzer: {atime}ms, Planner: {ptime}ms, Executor: {etime}ms')
        else:
            # Update all modules
            self.monitor.update(dt)
            self.analyzer.update(dt)
            self.planner.update(dt)
            self.executor.update(dt)

        return self.knowledge.state_machine.current_state

    def destroy(self):
        self.monitor.destroy()

    def reset(self):
        self.vehicle.apply_control(carla.VehicleControl())

    # Main interaction point with autopilot - set the destination, so that it does the rest
    def set_destination(self, destination):
        # Set destination in knowledge, so that planner can plan the route
        self.knowledge.update(destination=destination)

    def measure(self, func):
        start = int(round(time.time() * 1000))
        func()
        end = int(round(time.time() * 1000))

        return end - start
