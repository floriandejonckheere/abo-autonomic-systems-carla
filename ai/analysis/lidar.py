from ai.carla import carla

import numpy as np

from sklearn.cluster import DBSCAN


COLORS = [
    carla.Color(255, 0, 0),
    carla.Color(0, 255, 0),
    carla.Color(0, 0, 255),
    carla.Color(255, 255, 0),
    carla.Color(0, 255, 255),
    carla.Color(255, 0, 255),
    carla.Color(255, 255, 255),
    carla.Color(0, 0, 0),
]


class LIDAR:
    """
    Simple LIDAR sensor analyzer

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

    def analyze(self, image):
        data = np.frombuffer(image.raw_data, dtype=np.dtype('f4'))
        data = np.reshape(data, (int(data.shape[0] / 3), 3))
        data = data.copy()

        # Flip X and Y axes
        data[:, 0] = -data[:, 0]
        data[:, 1] = -data[:, 1]

        # Apply Z-axis offset (LIDAR sensor position)
        data[:, 2] = 2.5 - data[:, 2]

        # Decimate data
        data = data[::1]

        # Select only data above ground level (0.5 meters with offset of 2.5m)
        data = data[data[:, 2] > 0.5]

        if len(data) == 0:
            return

        # Cluster points based on density
        db = DBSCAN(eps=1.5, min_samples=10)
        db.fit(data)

        # Segment data based on labels
        clusters = np.hstack((data, db.labels_.reshape(-1, 1)))
        clusters = clusters[clusters[:, -1].argsort()]
        clusters = np.split(clusters[:, :-1], np.unique(clusters[:, -1], return_index=True)[1][1:])

        # Compute bounding box for each cluster
        for i, cluster in enumerate(clusters):
            x_offset = self.vehicle.get_transform().location.x
            y_offset = self.vehicle.get_transform().location.y
            z_offset = self.vehicle.get_transform().location.z

            x_min = np.min(cluster[:, 0]) + x_offset
            x_max = np.max(cluster[:, 0]) + x_offset
            y_min = np.min(cluster[:, 1]) + y_offset
            y_max = np.max(cluster[:, 1]) + y_offset
            z_min = np.min(cluster[:, 2]) + z_offset
            z_max = np.max(cluster[:, 2]) + z_offset

            # Plot bounding box
            if self.debug and self.knowledge.draw_lines:

                centroid = carla.Location(x=(x_max - x_min) / 2 + x_min, y=(y_max - y_min) / 2 + y_min, z=(z_max - z_min) / 2 + z_min)

                # self.vehicle.get_world().debug.draw_point(centroid, size=2, color=COLORS[i], life_time=5)

                self.vehicle.get_world().debug.draw_line(carla.Location(x_min, y_min, z_min), carla.Location(x_min, y_min, z_max), color=COLORS[i], life_time=5)
                self.vehicle.get_world().debug.draw_line(carla.Location(x_min, y_max, z_min), carla.Location(x_min, y_max, z_max), color=COLORS[i], life_time=5)
                self.vehicle.get_world().debug.draw_line(carla.Location(x_max, y_min, z_min), carla.Location(x_max, y_min, z_max), color=COLORS[i], life_time=5)
                self.vehicle.get_world().debug.draw_line(carla.Location(x_max, y_max, z_min), carla.Location(x_max, y_max, z_max), color=COLORS[i], life_time=5)

                self.vehicle.get_world().debug.draw_line(carla.Location(x_min, y_min, z_min), carla.Location(x_max, y_min, z_min), color=COLORS[i], life_time=5)
                self.vehicle.get_world().debug.draw_line(carla.Location(x_min, y_min, z_max), carla.Location(x_max, y_min, z_max), color=COLORS[i], life_time=5)
                self.vehicle.get_world().debug.draw_line(carla.Location(x_min, y_max, z_min), carla.Location(x_max, y_max, z_min), color=COLORS[i], life_time=5)
                self.vehicle.get_world().debug.draw_line(carla.Location(x_min, y_max, z_max), carla.Location(x_max, y_max, z_max), color=COLORS[i], life_time=5)

                self.vehicle.get_world().debug.draw_line(carla.Location(x_min, y_min, z_min), carla.Location(x_min, y_max, z_min), color=COLORS[i], life_time=5)
                self.vehicle.get_world().debug.draw_line(carla.Location(x_min, y_min, z_max), carla.Location(x_min, y_max, z_max), color=COLORS[i], life_time=5)
                self.vehicle.get_world().debug.draw_line(carla.Location(x_max, y_min, z_min), carla.Location(x_max, y_max, z_min), color=COLORS[i], life_time=5)
                self.vehicle.get_world().debug.draw_line(carla.Location(x_max, y_min, z_max), carla.Location(x_max, y_max, z_max), color=COLORS[i], life_time=5)

        self.knowledge.draw_lines = False
