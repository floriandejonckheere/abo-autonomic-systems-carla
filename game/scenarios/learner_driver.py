from ai.carla import carla

import threading
import time

from .scenario import Scenario

import game.utils as utils


class LearnerDriver(Scenario):
    """Straight towards the roundabout, wait behind a learner driver, then enter and drive a bit."""

    waypoints = [
        carla.Location(42.5959, -4.3443, 1.8431),
        carla.Location(22, -4, 1.8431),
        carla.Location(9, -22, 1.8431),
    ]

    def __init__(self, world):
        super().__init__(world)

        self.learner = None

    def setup(self):
        spawn_point = carla.Transform(location=carla.Location(25.6482, -5, 1.8431),  rotation=carla.Rotation(yaw=185))

        learner = utils.try_spawn_random_vehicle_at(self.world, spawn_point)
        self.actors.append(learner)

        bp = self.world.get_blueprint_library().find('sensor.other.collision')
        sensor = self.world.spawn_actor(bp, carla.Transform(), attach_to=learner)
        self.actors.append(sensor)

        def _on_collision(self, event):
            if not self:
                return
            print('Collision with: ', event.other_actor.type_id)
            if event.other_actor.type_id.split('.')[0] == 'vehicle':
                print("Test FAILED")

            sensor.destroy()

        sensor.listen(lambda event: _on_collision(learner, event))

        def learner_control():
            # Wait for a while, then drive onto the roundabout the wrong way
            time.sleep(5)

            # Drive onto the roundabout the wrong way
            learner.is_alive and learner.apply_control(carla.VehicleControl(throttle=1.0, steer=-0.4))

            time.sleep(3)

            # Stop the learner
            learner.is_alive and learner.apply_control(carla.VehicleControl(brake=1.0))

        self.learner = threading.Thread(target=learner_control)
        self.learner.start()

    def destroy(self):
        self.learner.join()

        super().destroy()

