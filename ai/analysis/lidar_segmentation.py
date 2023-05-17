from ai.carla import carla

import time

import numpy as np

from sklearn.cluster import DBSCAN

from .bounding_box import BoundingBox


class LIDARSegmentation:
    """
    Simple LIDAR sensor analyzer (segmenter)

    This analyzer is responsible for analyzing LIDAR sensor data and detecting obstacles.
    It uses DBSCAN clustering algorithm to group points into clusters and then computes
    the bounding box for each cluster. The bounding box is then used to determine the
    obstacle's position and size.

    The LIDAR sensor data needs to be processed in order to be usable. The data is
    first converted to a numpy array and then reshaped to a 2D array with 3 columns
    for the three dimensions. In order for the coordinates to be projected onto the
    CARLA simulator, the axes need to be flipped and the Z-axis offset needs to be
    applied (position of the LIDAR sensor relative to the vehicle).
    """


    def __init__(self, knowledge, vehicle, debug):
        self.knowledge = knowledge
        self.vehicle = vehicle
        self.debug = debug

        self.last_render_at = 0

    def analyze(self, image):
        data = np.frombuffer(image.raw_data, dtype=np.dtype('f4'))
        data = np.reshape(data, (int(data.shape[0] / 3), 3))
        data = data.copy()

        # Flip X and Y axes
        data[:, 0] = -data[:, 0]
        data[:, 1] = -data[:, 1]

        # Apply Z-axis offset (LIDAR sensor position)
        data[:, 2] = 2.1 - data[:, 2]

        # Decimate data
        data = data[::1]

        # Select only data above ground level (0.1 meters with offset of 2.1m)
        data = data[data[:, 2] > 0.1]

        if len(data) == 0:
            return

        # Cluster points based on density
        db = DBSCAN(eps=1.1, min_samples=10)
        db.fit(data)

        # Segment data based on labels
        clusters = np.hstack((data, db.labels_.reshape(-1, 1)))
        clusters = clusters[clusters[:, -1].argsort()]
        clusters = np.split(clusters[:, :-1], np.unique(clusters[:, -1], return_index=True)[1][1:])

        bounding_boxes = []

        # Compute bounding box for each cluster
        for cluster in clusters:
            # Offset bounding box by vehicle's location
            x_offset = self.vehicle.get_transform().location.x
            y_offset = self.vehicle.get_transform().location.y
            z_offset = self.vehicle.get_transform().location.z

            x_min = np.min(cluster[:, 0]) + x_offset
            y_min = np.min(cluster[:, 1]) + y_offset
            z_min = np.min(cluster[:, 2]) + z_offset

            x_max = np.max(cluster[:, 0]) + x_offset
            y_max = np.max(cluster[:, 1]) + y_offset
            z_max = np.max(cluster[:, 2]) + z_offset

            bounding_boxes.append(BoundingBox(x_min, y_min, z_min, x_max, y_max, z_max))

        # Render bounding box periodically
        if self.debug and time.time() - self.last_render_at > 1:
            self.last_render_at = time.time()

            for bounding_box in bounding_boxes:
                bounding_box.render(self.vehicle.get_world())

        return bounding_boxes
