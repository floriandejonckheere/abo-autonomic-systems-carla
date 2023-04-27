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

        # Lane detector sensor
        bp = world.get_blueprint_library().find('sensor.other.lane_detector')
        self.lane_detector = world.spawn_actor(bp, carla.Transform(), attach_to=self.vehicle)
        self.lane_detector.listen(lambda event: Monitor._on_invasion(weak_self, event))

        # Collision sensor
        bp = world.get_blueprint_library().find('sensor.other.collision')
        self.collision_sensor = world.spawn_actor(bp, carla.Transform(), attach_to=self.vehicle)
        self.collision_sensor.listen(lambda event: Monitor._on_collision(weak_self, event))

        # Depth sensor
        bp = world.get_blueprint_library().find('sensor.camera.depth')
        bp.set_attribute('sensor_tick', '0.1')
        bp.set_attribute('image_size_x', '320')
        bp.set_attribute('image_size_y', '240')
        bp.set_attribute('fov', '30')  # Use a narrow field of view

        # Location of sensor is 1.6 meters from center of vehicle, 1 meter above ground
        location = carla.Location(x=1.6, z=1.0)

        self.depth_sensor = world.spawn_actor(bp, carla.Transform(location), attach_to=self.vehicle)
        self.depth_sensor.listen(lambda image: Monitor._on_depth(weak_self, image))

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

    def destroy(self):
        self.lane_detector.destroy()
        self.collision_sensor.destroy()
        self.depth_sensor.destroy()

    @staticmethod
    def _on_invasion(weak_self, event):
        self = weak_self()
        if not self:
            return

        self.knowledge.update(lane_invasion=event.crossed_lane_markings)

    @staticmethod
    def _on_collision(weak_self, event):
        self = weak_self()
        if not self:
            return

        self.knowledge.update(collision=event.other_actor.type_id)

    @staticmethod
    def _on_depth(weak_self, image):
        self = weak_self()
        if not self:
            return

        self.knowledge.depth_image = image
