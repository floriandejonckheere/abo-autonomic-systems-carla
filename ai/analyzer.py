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


# Analyzer is responsible for parsing all the data that the knowledge has received from Monitor and turning it into
# something usable
# TODO: During the update step parse the data inside knowledge into information that could be used by planner to plan
#  the route
class Analyzer(object):
    def __init__(self, knowledge):
        self.knowledge = knowledge

    # Function that is called at time intervals to update ai-state
    def update(self, time_elapsed):
        return
