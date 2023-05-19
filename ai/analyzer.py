from ai.carla import carla

from .analysis.lidar import LIDAR
from .analysis.proximity import Proximity

import time
import math

import numpy as np


class Analyzer(object):
    """Analyzer is responsible for parsing all the data that the knowledge has received from Monitor and turning it into something usable."""

    def __init__(self, knowledge, vehicle, debug):
        self.knowledge = knowledge
        self.vehicle = vehicle
        self.debug = debug

        # LIDAR analyzer
        self.lidar = LIDAR()

        # Left and right proximity sensors (mounted on the front corners of the car)
        self.proximity_left = Proximity(vehicle, x=self.vehicle.bounding_box.extent.x, y=self.vehicle.bounding_box.extent.y, z=0.5)
        self.proximity_right = Proximity(vehicle, x=self.vehicle.bounding_box.extent.x, y=-self.vehicle.bounding_box.extent.y, z=0.5)

    # Function that is called at time intervals to update ai-state
    def update(self, dt):
        # Stop analyzing if vehicle is parked
        if self.knowledge.state_machine.parked.is_active:
            return

        # Calculate speed
        self.knowledge.speed = 3.6 * math.sqrt(self.knowledge.velocity.x ** 2 + self.knowledge.velocity.y ** 2 + self.knowledge.velocity.z ** 2)

        # Save location history
        self.save_location()

        # Detect collision and transition to crashed state
        self.detect_collision()

        # Analyze depth camera data
        self.analyze_depth_image()

        # Analyze LIDAR sensor data
        self.analyze_lidar_image()

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

    def analyze_depth_image(self):
        array = np.frombuffer(self.knowledge.depth_image.raw_data, dtype=np.dtype("uint8"))
        array = np.reshape(array, (self.knowledge.depth_image.height, self.knowledge.depth_image.width, 4))
        array = array[:, :, :3]
        array = array[:, :, ::-1]

        # Proximity to obstacle in front
        self.knowledge.proximity = np.mean(array)

        # Check if obstacle is in front
        self.knowledge.obstacle = self.knowledge.proximity < 20

    def analyze_lidar_image(self):
        # Analyze LIDAR data and find potential obstacles
        obstacles = self.lidar.analyze(self.knowledge.lidar_image)

        # Proximity to obstacle on left and right (collision avoidance)
        self.knowledge.proximity_left = min([self.proximity_left.distance_to(obstacle) for obstacle in obstacles]) if len(obstacles) > 0 else 1000.0
        self.knowledge.proximity_right = min([self.proximity_right.distance_to(obstacle) for obstacle in obstacles]) if len(obstacles) > 0 else 1000.0

        # Check if obstacle is on left or right side
        self.knowledge.obstacle_left = self.knowledge.proximity_left < 2
        self.knowledge.obstacle_right = self.knowledge.proximity_right < 2

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
