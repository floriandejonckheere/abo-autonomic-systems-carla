from ai.carla import carla

from .scenario import Scenario

import game.utils as utils


class Crash(Scenario):
    """Unavoidable collision with a vehicle"""

    waypoints = [
        carla.Location(42.5959, -4.3443, 1.8431),
        carla.Location(22, -4, 1.8431),
        carla.Location(9, -22, 1.8431),
    ]

    def setup(self):
        spawn_point = carla.Transform(location=carla.Location(19.7, 12.3, 1.8431),  rotation=carla.Rotation(yaw=-71))
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
            kamikaze.destroy()

        sensor.listen(lambda event: _on_collision(kamikaze, event))

        kamikaze.apply_control(carla.VehicleControl(throttle=0.7))