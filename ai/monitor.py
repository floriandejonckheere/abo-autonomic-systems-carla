import weakref

from ai.carla import carla

import numpy as np


# Monitor is responsible for reading the data from the sensors and telling it to the knowledge
# TODO: Implement other sensors (lidar and depth sensors mainly)
class Monitor(object):
    def __init__(self, knowledge, vehicle, debug):
        self.vehicle = vehicle
        self.knowledge = knowledge
        self.debug = debug

        weak_self = weakref.ref(self)

        # Initialize knowledge values
        self.update(None)

        world = self.vehicle.get_world()

        # Lane detector sensor
        bp = world.get_blueprint_library().find('sensor.other.lane_detector')
        self.lane_detector = world.spawn_actor(bp, carla.Transform(), attach_to=self.vehicle)
        self.lane_detector.listen(lambda event: Monitor._on_invasion(weak_self, event))

        # Collision sensor
        bp = world.get_blueprint_library().find('sensor.other.collision')
        self.collision_sensor = world.spawn_actor(bp, carla.Transform(), attach_to=self.vehicle)
        self.collision_sensor.listen(lambda event: Monitor._on_collision(weak_self, event))

        # LIDAR sensor
        bp = world.get_blueprint_library().find('sensor.lidar.ray_cast')
        bp.set_attribute('sensor_tick', '0.1')

        # Location of sensor is on top of vehicle
        location = carla.Location(z=2.5)

        self.lidar_sensor = world.spawn_actor(bp, carla.Transform(location), attach_to=self.vehicle)
        self.lidar_sensor.listen(lambda image: Monitor._on_lidar(weak_self, image))

        # Proximity sensor
        bp = world.get_blueprint_library().find('sensor.camera.depth')
        bp.set_attribute('sensor_tick', '0.01')
        bp.set_attribute('image_size_x', '160')
        bp.set_attribute('image_size_y', '120')
        bp.set_attribute('fov', '25')

        # Location of sensor is front of vehicle, 1 meter above ground
        location = carla.Location(x=self.vehicle.bounding_box.extent.x, z=1.0)

        self.proximity = world.spawn_actor(bp, carla.Transform(location), attach_to=self.vehicle)
        self.proximity.listen(lambda image: Monitor._on_proximity(weak_self, image))

    # Function that is called at time intervals to update ai-state
    def update(self, dt):
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
        self.lidar_sensor.destroy()

        self.proximity.destroy()

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
    def _on_lidar(weak_self, image):
        self = weak_self()
        if not self:
            return

        self.knowledge.lidar_image = image

    @staticmethod
    def _on_proximity(weak_self, image):
        self = weak_self()
        if not self:
            return

        # Convert to grayscale
        image.convert(carla.ColorConverter.Depth)

        self.knowledge.proximity_image = image
