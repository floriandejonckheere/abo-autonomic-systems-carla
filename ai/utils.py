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
