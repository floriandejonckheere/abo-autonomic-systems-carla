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

import threading
import time

from .scenario import Scenario

import game.utils as utils


class StopAndGo(Scenario):
    """Stop-and-go traffic"""

    waypoints = [
        carla.Location(-6.5, 38.9, 1.8431),
        carla.Location(-5.4, 187.0, 1.8431),
    ]

    def __init__(self, world):
        super().__init__(world)

        self.thread = None
        self.running = True

        self.use_spawnpoint = False

    def setup(self):
        spawn_point = carla.Transform(location=carla.Location(-6.5, 61.6, 1.8431),  rotation=carla.Rotation(yaw=90))

        car = utils.try_spawn_random_vehicle_at(self.world, spawn_point)
        self.actors.append(car)

        bp = self.world.get_blueprint_library().find('sensor.other.collision')
        sensor = self.world.spawn_actor(bp, carla.Transform(), attach_to=car)
        self.actors.append(sensor)

        def _on_collision(self, event):
            if not self:
                return
            print('Collision with: ', event.other_actor.type_id)
            if event.other_actor.type_id.split('.')[0] == 'vehicle':
                print("Test FAILED")

            sensor.destroy()

        sensor.listen(lambda event: _on_collision(car, event))

        def learner_control():
            while self.running:
                # Drive forward
                car.is_alive and car.apply_control(carla.VehicleControl(throttle=0.5, steer=0.0))

                time.sleep(2)

                if not self.running:
                    break

                # Brake
                car.is_alive and car.apply_control(carla.VehicleControl(brake=1.0))

                time.sleep(2)

        self.thread = threading.Thread(target=learner_control)
        self.thread.start()

    def destroy(self):
        self.running = False
        self.thread.join()

        super().destroy()

