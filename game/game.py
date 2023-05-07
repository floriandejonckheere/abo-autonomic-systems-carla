from ai.carla import carla

from ai.autopilot import Autopilot

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

        if self.debug:
            # Render waypoints
            for i, wp in enumerate(self.waypoints):
                self.world.debug.draw_string(wp, f'WP {i}', draw_shadow=False,
                                             color=carla.Color(r=255, g=0, b=0), life_time=20.0,
                                             persistent_lines=True)

        # Getting waypoint to spawn
        if self.scenario.use_spawnpoint:
            start = self.get_start_point(self.waypoints[0])
        else:
            start = self.world.get_map().get_waypoint(self.waypoints[0])

        # Spawn vehicle
        vehicle = utils.try_spawn_random_vehicle_at(self.world, start.transform)

        vehicle and self.actors.append(vehicle)

        if vehicle is None:
            raise Exception("Could not spawn vehicle")

        # Set up scenario
        self.scenario.setup()

        # Set up autopilot
        self.autopilot = Autopilot(vehicle, self.debug)
        self.autopilot.set_destination(destination)

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
        # Handle only arrived state change
        if target is not self.autopilot.knowledge.state_machine.arrived:
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
