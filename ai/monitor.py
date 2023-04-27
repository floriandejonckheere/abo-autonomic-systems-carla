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

import weakref
import carla


# Monitor is responsible for reading the data from the sensors and telling it to the knowledge
# TODO: Implement other sensors (lidar and depth sensors mainly)
class Monitor(object):
    def __init__(self, knowledge, vehicle):
        self.vehicle = vehicle
        self.knowledge = knowledge
        weak_self = weakref.ref(self)

        # Initialize knowledge values
        self.update()

        world = self.vehicle.get_world()
        bp = world.get_blueprint_library().find('sensor.other.lane_detector')
        self.lane_detector = world.spawn_actor(bp, carla.Transform(), attach_to=self.vehicle)
        self.lane_detector.listen(lambda event: Monitor._on_invasion(weak_self, event))

    # Function that is called at time intervals to update ai-state
    def update(self):
        self.knowledge.update(
            location=self.vehicle.get_transform().location,
            rotation=self.vehicle.get_transform().rotation,
            velocity=self.vehicle.get_velocity(),
            target_speed=self.vehicle.get_speed_limit(),
            is_at_traffic_light=self.vehicle.is_at_traffic_light(),
            traffic_light=self.vehicle.get_traffic_light(),
        )

    @staticmethod
    def _on_invasion(weak_self, event):
        self = weak_self()
        if not self:
            return
        self.knowledge.update(lane_invasion=event.crossed_lane_markings)
