from threading import Timer

from ai.carla import carla

from collections import deque

from ai.autopilot import Autopilot

import game.utils as utils
import game.scenarios as scenarios


class Simulation:
    """Simulation is responsible for setting up a scenario and running the simulation."""

    def __init__(self, world, debug, profile, scenario):
        self.world = world
        self.debug = debug
        self.profile = profile
        self.scenario = scenario

        self.autopilot = None
        self.actors = []

        self.running = True
        self.counter = 0

    def setup(self):
        # Instantiate scenario
        klass = getattr(scenarios, self.scenario)

        if not issubclass(klass, scenarios.Scenario):
            raise Exception(f'Invalid scenario: {self.scenario}')

        self.scenario = klass(self.world)

        # Starting point is first waypoint
        first = self.scenario.next_waypoint()

        # First destination is second waypoint
        second = self.scenario.next_waypoint()

        if first is None or second is None:
            raise Exception('Scenario needs at least 2 waypoints')

        # Getting waypoint to spawn
        if self.scenario.use_spawnpoint:
            start = self.get_start_point(first)
        else:
            start = self.world.get_map().get_waypoint(first)

        # Spawn vehicle
        vehicle = utils.try_spawn_random_vehicle_at(self.world, start.transform)

        if vehicle is None:
            raise Exception('Could not spawn vehicle')

        self.actors.append(vehicle)

        # Set up scenario
        self.scenario.setup()

        # Set up autopilot
        self.autopilot = Autopilot(vehicle, self.debug, self.profile)
        self.autopilot.set_destination(second)

        # Set up callback for destination arrival
        self.autopilot.knowledge.state_machine.add_observer(self)

    def tick(self):
        # Update autopilot
        status = self.autopilot.update()

        if status is None:
            self.counter += 1

            if self.counter > 3:
                self.running = False
            else:
                self.counter = 0

    def destroy(self):
        print('Exiting...')

        for actor in self.actors:
            actor.is_alive and actor.destroy()

        self.autopilot and self.autopilot.destroy()

        self.scenario and self.scenario.destroy()

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

    def after_transition(self, event, source, target):
        if target is self.autopilot.knowledge.state_machine.arrived:
            # Check if vehicle arrived at destination
            pos = self.autopilot.vehicle.get_transform().location
            print(f'Vehicle arrived at destination: {pos}')

            if pos.distance(carla.Location(self.autopilot.knowledge.destination)) < 5.0:
                waypoint = self.scenario.next_waypoint()

                if waypoint is None:
                    print('Excercise route finished')

                    # Park car (final destination reached)
                    self.autopilot.knowledge.state_machine.park()

                    # Stop autopilot
                    # self.running = False
                else:
                    # Set next destination
                    self.autopilot.set_destination(waypoint)
        elif target is self.autopilot.knowledge.state_machine.waiting:
            # Turn traffic light green after 2 seconds
            Timer(2, self.autopilot.vehicle.get_traffic_light().set_state, [carla.TrafficLightState.Green]).start()
