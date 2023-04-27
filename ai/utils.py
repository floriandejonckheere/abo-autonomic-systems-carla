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

import carla

import numpy as np


def distance(vec1, vec2):
    l1 = carla.Location(vec1)
    l2 = carla.Location(vec2)
    return l1.distance(l2)


def angle(source_vector, target_vector):
    # Normalize source and target vectors
    source_vector /= np.linalg.norm(source_vector)
    target_vector /= np.linalg.norm(target_vector)

    # Calculate dot product between vectors
    dot_product = np.dot(source_vector, target_vector)

    # Calculate cross product between vectors
    cross_product = np.cross(source_vector, target_vector)

    # Calculate angle in radians
    angle_radians = np.arccos(dot_product)

    # Determine direction of angle using cross product
    if cross_product < 0:
        angle_radians = -angle_radians

    # Convert angle from radians to degrees
    return np.degrees(angle_radians)
