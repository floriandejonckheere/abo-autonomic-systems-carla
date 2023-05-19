from ai.carla import carla

import threading
import time

from .scenario import Scenario

import game.utils as utils


class Kamikaze(Scenario):
    """Straight towards the roundabout, enter, and avoid the kamikaze."""

    waypoints = [
        carla.Location(42.5959, -4.3443, 1.8431),
        carla.Location(22, -4, 1.8431),
        # carla.Location(9, -22, 1.8431),
        carla.Location(-14, 14.6, 1.8431),
    ]

    def __init__(self, world):
        super().__init__(world)

        self.learner = None

    def setup(self):
        spawn_point = carla.Transform(location=carla.Location(4.4, -40.7, 1.8431),  rotation=carla.Rotation(yaw=85))

        kamikaze = utils.try_spawn_random_vehicle_at(self.world, spawn_point)
        self.actors.append(kamikaze)

        bp = self.world.get_blueprint_library().find('sensor.other.collision')
        sensor = self.world.spawn_actor(bp, carla.Transform(), attach_to=kamikaze)
        self.actors.append(sensor)

        def _on_collision(self, event):
            if not self:
                return
            print('Collision with: ', event.other_actor.type_id)
            if event.other_actor.type_id.split('.')[0] == 'vehicle':
                print("Test FAILED")

            sensor.destroy()

        sensor.listen(lambda event: _on_collision(kamikaze, event))

        def learner_control():
            # Wait for a while, then drive onto the roundabout the wrong way
            time.sleep(4)

            # Drive onto the roundabout the wrong way
            kamikaze.is_alive and kamikaze.apply_control(carla.VehicleControl(throttle=1.0))

            time.sleep(5)

            # Stop the learner
            kamikaze.is_alive and kamikaze.apply_control(carla.VehicleControl(brake=1.0))

        self.learner = threading.Thread(target=learner_control)
        self.learner.start()

    def destroy(self):
        self.learner.join()

        super().destroy()

