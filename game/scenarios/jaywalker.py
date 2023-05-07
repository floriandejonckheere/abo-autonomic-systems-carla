from ai.carla import carla

from .scenario import Scenario

import game.utils as utils


class Jaywalker(Scenario):
    """Jaywalker crossing the road"""

    waypoints = [
        carla.Location(-6.5, 38.9, 1.8431),
        carla.Location(-5.4, 187.0, 1.8431),
    ]

    def __init__(self, world):
        super().__init__(world)

        self.use_spawnpoint = False

    def setup(self):
        spawn_point = carla.Transform(location=carla.Location(-12, 65, 1.8431),  rotation=carla.Rotation(yaw=90))

        walker = utils.try_spawn_random_walker_at(self.world, spawn_point)
        self.actors.append(walker)

        bp = self.world.get_blueprint_library().find('sensor.other.collision')
        sensor = self.world.spawn_actor(bp, carla.Transform(), attach_to=walker)
        self.actors.append(sensor)

        def _on_collision(self, event):
            if not self:
                return
            print('Collision with: ', event.other_actor.type_id)
            if event.other_actor.type_id.split('.')[0] == 'vehicle':
                print("Test FAILED")

            sensor.destroy()

        sensor.listen(lambda event: _on_collision(walker, event))

        # Walk forward
        walker.apply_control(carla.WalkerControl(speed=1.0))
