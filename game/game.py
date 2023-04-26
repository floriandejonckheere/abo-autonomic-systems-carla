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

import random

from ai.autopilot import Autopilot
from ai.event_broker import event_broker


class Game:
    EX1 = [carla.Location(42.5959, -4.3443, 1.8431), carla.Location(22, -4, 1.8431), carla.Location(9, -22, 1.8431)]
    EX2 = [carla.Location(42.5959, -4.3443, 1.8431), carla.Location(-30, 167, 1.8431)]
    EX3 = [carla.Location(42.5959, -4.3443, 1.8431), carla.Location(22, -4, 1.8431), carla.Location(9, -22, 1.8431)]

    # EX4 = [ carla.Location(42.5959,-4.3443,1.8431), carla.Location(134,-3,1.8431)]

    # KZS2 = carla.Location(-85,-23,1.8431)

    MILESTONES = [EX1, EX2, EX3]

    def __init__(self, world, debug, milestone_number):
        self.world = world
        self.debug = debug
        self.milestone_number = milestone_number

        self.autopilot = None
        self.actors = []
        self.waypoints = []

        self.running = True
        self.counter = 0

    def setup(self):
        # Setup waypoints
        ms = max(0, min(self.milestone_number - 1, len(self.MILESTONES) - 1))
        self.waypoints = self.MILESTONES[ms]

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

        # Spawning
        vehicle = self.try_spawn_random_vehicle_at(start.transform)

        if vehicle is None:
            raise Exception("Could not spawn vehicle")

        # Set up autopilot
        self.autopilot = Autopilot(vehicle)
        self.autopilot.set_destination(destination)

        # Set up callback for destination arrival
        event_broker.subscribe('state_changed', self.state_changed)

        # Spawn kamikaze for milestone 2
        if ms == 2:
            self.spawn_kamikaze(start.get_right_lane())

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

    def try_spawn_random_vehicle_at(self, transform, recursion=0):
        blueprints = self.world.get_blueprint_library().filter('vehicle.*')
        blueprints = [x for x in blueprints if int(x.get_attribute('number_of_wheels')) == 4]
        blueprints = [x for x in blueprints if not x.id.endswith('isetta')]

        blueprint = random.choice(blueprints)
        if blueprint.has_attribute('color'):
            color = random.choice(blueprint.get_attribute('color').recommended_values)
            blueprint.set_attribute('color', color)
        blueprint.set_attribute('role_name', 'autopilot')
        vehicle = self.world.try_spawn_actor(blueprint, transform)
        if vehicle is not None:
            self.actors.append(vehicle)
            print('spawned %r at %s' % (vehicle.type_id, transform.location))
        else:
            if recursion > 20:
                print('WARNING: vehicle not spawned, NONE returned')
            else:
                return self.try_spawn_random_vehicle_at(transform, recursion + 1)
        return vehicle

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
            self.running = False
        else:
            # Set next destination
            self.autopilot.set_destination(self.waypoints[-1])

    def spawn_kamikaze(self, spawn_point):
        kamikaze = self.try_spawn_random_vehicle_at(spawn_point.transform)
        bp = self.world.get_blueprint_library().find('sensor.other.collision')
        sensor = self.world.spawn_actor(bp, carla.Transform(), attach_to=kamikaze)

        def _on_collision(self, event):
            if not self:
                return
            print('Collision with: ', event.other_actor.type_id)
            if event.other_actor.type_id.split('.')[0] == 'vehicle':
                print("Test FAILED")
            kamikaze.destroy()
            sensor.destroy()

        sensor.listen(lambda event: _on_collision(kamikaze, event))

        control = carla.VehicleControl()
        control.throttle = 1.0
        control.steer = -0.07
        control.brake = 0.0
        control.hand_brake = False
        kamikaze.apply_control(control)
