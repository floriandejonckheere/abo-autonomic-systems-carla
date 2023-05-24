from ai.carla import carla

from .scenario import Scenario

import game.utils as utils

from threading import Timer


class Crash(Scenario):
    """Unavoidable collision with a vehicle."""

    WAYPOINTS = [
        carla.Location(42.5959, -4.3443, 1.8431),
        carla.Location(-30, 167, 1.8431),
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

            sensor.destroy()
            kamikaze.destroy()

        sensor.listen(lambda event: _on_collision(kamikaze, event))

        Timer(1.8, kamikaze.apply_control, [carla.VehicleControl(throttle=1.0)]).start()
