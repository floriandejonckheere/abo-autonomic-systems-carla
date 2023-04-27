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

from .scenario import Scenario

import game.utils as utils


class MilestoneThree(Scenario):
    """Straight towards the roundabout, avoid the kamikaze, then enter and drive a bit"""

    waypoints = [
        carla.Location(42.5959, -4.3443, 1.8431),
        carla.Location(22, -4, 1.8431),
        carla.Location(9, -22, 1.8431),
    ]

    def setup(self):
        spawn_point = carla.Transform(location=carla.Location(42.6482, -7.84391, 1.8431),  rotation=carla.Rotation(pitch=360, yaw=180.856))
        kamikaze = utils.try_spawn_random_vehicle_at(self.world, spawn_point)
        self.actors.append(kamikaze)

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