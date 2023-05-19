import weakref

from ai.carla import carla


class Monitor(object):
    """Monitor is responsible for reading the data from the sensors and updating the knowledge."""

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
        self.lane_detector.listen(lambda event: self.knowledge.update(lane_invasion=event.crossed_lane_markings))

        # Collision sensor
        bp = world.get_blueprint_library().find('sensor.other.collision')
        self.collision_sensor = world.spawn_actor(bp, carla.Transform(), attach_to=self.vehicle)
        self.collision_sensor.listen(lambda event: self.knowledge.update(collision=event.other_actor.type_id))

        # LIDAR sensor
        bp = world.get_blueprint_library().find('sensor.lidar.ray_cast')
        bp.set_attribute('sensor_tick', '0.1')

        # Location of sensor is on top of vehicle
        location = carla.Location(z=2.5)

        self.lidar_sensor = world.spawn_actor(bp, carla.Transform(location), attach_to=self.vehicle)
        self.lidar_sensor.listen(lambda image: self.knowledge.update(lidar_image=image))

        # Proximity sensors
        bp = world.get_blueprint_library().find('sensor.camera.depth')
        bp.set_attribute('sensor_tick', '0.01')
        bp.set_attribute('image_size_x', '160')
        bp.set_attribute('image_size_y', '120')
        bp.set_attribute('fov', '25')

        # Location of sensor is front of vehicle, 1 meter above ground
        location = carla.Location(x=self.vehicle.bounding_box.extent.x, z=1.0)

        self.proximity = world.spawn_actor(bp, carla.Transform(location), attach_to=self.vehicle)
        self.proximity.listen(lambda image: Monitor._on_proximity(weak_self, image))

        bp.set_attribute('fov', '10')

        self.proximity_left = world.spawn_actor(bp, carla.Transform(location, carla.Rotation(yaw=-45.0)), attach_to=self.vehicle)
        self.proximity_left.listen(lambda image: Monitor._on_proximity(weak_self, image, 'left'))

        self.proximity_right = world.spawn_actor(bp, carla.Transform(location, carla.Rotation(yaw=45.0)), attach_to=self.vehicle)
        self.proximity_right.listen(lambda image: Monitor._on_proximity(weak_self, image, 'right'))

        # RGB camera (top-down)
        bp = world.get_blueprint_library().find('sensor.camera.rgb')
        bp.set_attribute('sensor_tick', '0.1')
        bp.set_attribute('image_size_x', '160')
        bp.set_attribute('image_size_y', '120')

        # Location of sensor is above vehicle, looking down
        location = carla.Location(z=7.5)
        rotation = carla.Rotation(pitch=-90, yaw=-90)

        self.rgb_camera = world.spawn_actor(bp, carla.Transform(location, rotation), attach_to=self.vehicle)
        self.rgb_camera.listen(lambda image: self.knowledge.update(rgb_image=image))

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
        self.proximity_left.destroy()
        self.proximity_right.destroy()

    @staticmethod
    def _on_proximity(weak_self, image, orientation='front'):
        self = weak_self()
        if not self:
            return

        # Convert to grayscale
        image.convert(carla.ColorConverter.LogarithmicDepth)

        if orientation == 'front':
            self.knowledge.proximity_image = image
        elif orientation == 'left':
            self.knowledge.proximity_image_left = image
        elif orientation == 'right':
            self.knowledge.proximity_image_right = image
