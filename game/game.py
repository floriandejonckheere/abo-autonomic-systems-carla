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

from ai.autopilot import Autopilot
from ai.event_broker import event_broker

import game.utils as utils

import game.scenarios as scenarios

class Game:
    def __init__(self, world, debug, scenario):
        self.world = world
        self.debug = debug
        self.scenario = scenario

        self.autopilot = None
        self.actors = []
        self.waypoints = []

        self.running = True
        self.counter = 0

    def setup(self):
        # Instantiate scenario
        klass = getattr(scenarios, self.scenario)

        if not issubclass(klass, scenarios.Scenario):
            raise Exception(f'Invalid scenario: {self.scenario}')

        self.scenario = klass(self.world)

        # Setup waypoints
        self.waypoints = self.scenario.waypoints

        # First destination is second waypoint
        destination = self.waypoints[1]

        # Render waypoints
        if self.debug:
            for i, wp in enumerate(self.waypoints):
                self.world.debug.draw_string(wp, str(i), draw_shadow=False,
                                             color=carla.Color(r=255, g=0, b=0), life_time=20.0,
                                             persistent_lines=True)

        # Getting waypoint to spawn
        start = self.get_start_point(self.waypoints[0])

        # Spawn vehicle
        vehicle = utils.try_spawn_random_vehicle_at(self.world, start.transform)
        self.actors.append(vehicle)

        if vehicle is None:
            raise Exception("Could not spawn vehicle")

        # Set up scenario
        self.scenario.setup()

        # Set up autopilot
        self.autopilot = Autopilot(vehicle)
        self.autopilot.set_destination(destination)

        # Set up callback for destination arrival
        event_broker.subscribe('state_changed', self.state_changed)

    def tick(self):
        # Update autopilot
        status = self.autopilot.update()

        if status is None:
            self.counter += 1

            if self.counter > 3:
                self.running = False
            else:
                self.counter = 0

    def stop(self):
        print('Exiting...')

        for actor in self.actors:
            actor.is_alive and actor.destroy()

        self.scenario.teardown()

    def get_start_point(self, coord):
        points = self.world.get_map().get_spawn_points()
        index = 0
        ti = -1
        td = points[0].location.distance(coord)
        for point in points:
            ti += 1
            d = point.location.distance(coord)
            if d < td:
                td = d
                index = ti
        start_point = points[index]
        return self.world.get_map().get_waypoint(start_point.location)

    def state_changed(self, event):
        # Handle only arrived state change
        if event['state'] is not 'arrived':
            return

        pos = self.autopilot.vehicle.get_transform().location
        print("Vehicle arrived at destination: ", pos)
        if pos.distance(carla.Location(self.waypoints[-1])) < 5.0:
            print("Excercise route finished")

            # Park car (final destination reached)
            self.autopilot.knowledge.state_machine.park()

            # Stop autopilot
            # self.running = False
        else:
            # Set next destination
            self.autopilot.set_destination(self.waypoints[-1])
