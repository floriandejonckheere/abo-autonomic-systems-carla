import numpy as np

from sklearn.linear_model import RANSACRegressor
from sklearn.cluster import DBSCAN

from .obstacle import Obstacle


class LIDAR:
    """
    Simple LIDAR sensor analyzer (segmenter)

    This analyzer is responsible for analyzing LIDAR sensor data and detecting obstacles.
    It uses DBSCAN clustering algorithm to group points into clusters and then computes
    the bounding box for each cluster. The bounding box is then used to determine the
    obstacle's proximity.

    The LIDAR sensor data needs to be processed in order to be usable. The data is
    first converted to a numpy array and then reshaped to a 2D array with 3 columns
    for the three dimensions. In order for the coordinates to be projected onto the
    CARLA simulator, the axes need to be flipped and the Z-axis offset needs to be
    applied (position of the LIDAR sensor relative to the vehicle).
    """


    def analyze(self, image):
        data = np.frombuffer(image.raw_data, dtype=np.dtype('f4'))
        data = np.reshape(data, (int(data.shape[0] / 3), 3))
        data = data.copy()

        # Flip X and Y axes
        data[:, 0] = -data[:, 0]
        data[:, 1] = -data[:, 1]

        # Apply Z-axis offset (LIDAR sensor position)
        data[:, 2] = 2.5 - data[:, 2]

        # Remove ground plane using RANSAC (RANdom SAmple Consensus) algorithm
        # https://en.wikipedia.org/wiki/RANSAC
        ransac = RANSACRegressor(residual_threshold=0.5)
        ransac.fit(data[:, :2], data[:, 2])

        # Remove ground plane points
        data = data[np.logical_not(ransac.inlier_mask_)]

        # No data points left
        if len(data) == 0:
            return []

        # Cluster points using DBSCAN (Density-Based Spatial Clustering of Applications with Noise) algorithm
        # https://en.wikipedia.org/wiki/DBSCAN
        db = DBSCAN(eps=1.1, min_samples=10)
        db.fit(data)

        # Segment data based on labels
        clusters = np.hstack((data, db.labels_.reshape(-1, 1)))
        clusters = clusters[clusters[:, -1].argsort()]
        clusters = np.split(clusters[:, :-1], np.unique(clusters[:, -1], return_index=True)[1][1:])

        obstacles = []

        # Compute bounding box for each cluster
        for cluster in clusters:
            x_min = np.min(cluster[:, 0])
            y_min = np.min(cluster[:, 1])
            z_min = np.min(cluster[:, 2])

            x_max = np.max(cluster[:, 0])
            y_max = np.max(cluster[:, 1])
            z_max = np.max(cluster[:, 2])

            obstacle = Obstacle(x_min, y_min, z_min, x_max, y_max, z_max)

            # Consider only obstacles with some volume (excludes false positives like lantern poles and traffic signs)
            if obstacle.volume() > 0.1:
                obstacles.append(obstacle)

        return obstacles
