from ai.carla import carla

import time

from .bounding_box import BoundingBox


class LIDARCollision:
    """
    LIDAR collision detector.

    This analyzer is responsible for analyzing bounding box data and detecting obstacles.
    """

    def __init__(self, knowledge, vehicle, debug):
        self.knowledge = knowledge
        self.vehicle = vehicle
        self.debug = debug

        self.last_render_at = 0

        # Collision detection boxes
        self.front = BoundingBox(-1.2, 7.5, 0.0, 1.2, 2.5, 2.0)
        self.left = BoundingBox(-1.2, 5, 0.0, -2.4, 0, 2.0)
        self.right = BoundingBox(1.2, 5, 0.0, 2.4, 0, 2.0)

    def analyze(self, bounding_boxes):
        # Detect obstacles in front
        for bounding_box in bounding_boxes:
            if self.front.collides_with(bounding_box):
                distance = self.vehicle.get_location().distance(bounding_box.centroid)
                self.knowledge.obstacles.append(bounding_box)

                print(f'Obstacle in front: ({bounding_box.centroid.x:.2f}, {bounding_box.centroid.y:.2f}, {bounding_box.centroid.z:.2f}) at distance {distance:.2f}')

        # Render bounding box periodically
        if self.debug and time.time() - self.last_render_at > 1:
            self.last_render_at = time.time()

            self.front.render(self.vehicle, color=carla.Color(255, 255, 0))
            self.left.render(self.vehicle, color=carla.Color(255, 255, 0))
            self.right.render(self.vehicle, color=carla.Color(255, 255, 0))
