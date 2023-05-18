from ai.carla import carla

from .analysis.bounding_box import BoundingBox
from .analysis.lidar import LIDAR
from .analysis.proximity import Proximity

import time

import numpy as np


# Analyzer is responsible for parsing all the data that the knowledge has received from Monitor and turning it into something usable
class Analyzer(object):
    def __init__(self, knowledge, vehicle, debug):
        self.knowledge = knowledge
        self.vehicle = vehicle
        self.debug = debug

        # LIDAR analyzer
        self.lidar = LIDAR()

        # Left and right proximity sensors (mounted on the front corners of the car)
        self.left = Proximity(vehicle, x=self.vehicle.bounding_box.extent.x, y=self.vehicle.bounding_box.extent.y, z=0.5, r=2.0)
        self.right = Proximity(vehicle, x=self.vehicle.bounding_box.extent.x, y=-self.vehicle.bounding_box.extent.y, z=0.5, r=2.0)

    # Function that is called at time intervals to update ai-state
    def update(self, dt):
        self.left.render(color=carla.Color(0, 255, 0))
        self.right.render(color=carla.Color(0, 0, 255))

        # Stop analyzing if vehicle is parked
        if self.knowledge.state_machine.parked.is_active:
            return

        # Save location history
        self.save_location()

        # Detect collision and transition to crashed state
        self.detect_collision()

        # Analyze LIDAR sensor data
        self.analyze_lidar_image()

        # Analyze depth camera data
        self.analyze_depth_image()

        # Avoid collisions and transition to healing state
        # self.avoid_collision()

    def save_location(self):
        # Save location history periodically
        if not self.knowledge.last_location_at or time.time() - self.knowledge.last_location_at > 0.5:
            # Save location only if vehicle is driving
            if not self.knowledge.state_machine.driving.is_active:
                return

            # Save location if vehicle has moved more than 2 meters
            if len(self.knowledge.location_history) != 0 and self.knowledge.location_history[-1].distance(self.knowledge.location) < 1.0:
                return

            self.knowledge.last_location_at = time.time()
            self.knowledge.location_history.append(self.knowledge.location)

    def detect_collision(self):
        if self.knowledge.collision and not self.knowledge.state_machine.crashed.is_active and not self.knowledge.state_machine.recovering.is_active:
            # Clear collision state
            self.knowledge.collision = False

            # Transition to crashed state
            self.knowledge.state_machine.crash()

    def analyze_lidar_image(self):
        # Analyze LIDAR data and find potential obstacles
        self.knowledge.obstacles = self.lidar.analyze(self.knowledge.lidar_image)

    def analyze_depth_image(self):
        # Proximity to obstacle in front (cruise control)
        self.knowledge.proximity = np.mean(self.convert_proximity_image(self.knowledge.proximity_image))
        self.knowledge.obstacle = self.knowledge.proximity < 20

        # Proximity to obstacle on left and right (collision avoidance)
        if len(self.knowledge.obstacles) > 0:
            self.knowledge.proximity_left = min([self.left.distance_to(obstacle) for obstacle in self.knowledge.obstacles])
            self.knowledge.obstacle_left = self.knowledge.proximity_left < 2.0

            self.knowledge.proximity_right = min([self.right.distance_to(obstacle) for obstacle in self.knowledge.obstacles])
            self.knowledge.obstacle_right = self.knowledge.proximity_right < 2.0
        else:
            self.knowledge.proximity_left = 1000.0
            self.knowledge.proximity_right = 1000.0

    def convert_proximity_image(self, image):
        array = np.frombuffer(image.raw_data, dtype=np.dtype("uint8"))
        array = np.reshape(array, (image.height, image.width, 4))
        array = array[:, :, :3]
        array = array[:, :, ::-1]

        return array

    def avoid_collision(self):
        # Do not avoid collision if already crashed or recovering
        if self.knowledge.state_machine.crashed.is_active or self.knowledge.state_machine.recovering.is_active:
            return

        if self.knowledge.state_machine.healing.is_active:
            last_event, timestamp = self.knowledge.state_machine.history[-1]

            # Go back to driving if healing timeout has passed
            if time.time() - timestamp > 5.0:
                self.knowledge.state_machine.drive()
        else:
            # Avoid collision if proximity is too low
            if self.knowledge.obstacle or self.knowledge.obstacle_left or self.knowledge.obstacle_right:
                self.knowledge.state_machine.heal()
