import glob
import os
import sys
import math

try:
    sys.path.append(glob.glob('../**/*%d.%d-%s.egg' % (
        sys.version_info.major,
        sys.version_info.minor,
        'win-amd64' if os.name == 'nt' else 'linux-x86_64'))[0])
except IndexError:
    pass

from enum import Enum

import carla

import ai.utils as utils


class Status(Enum):
    ARRIVED = 0
    DRIVING = 1
    CRASHED = 2
    HEALING = 3
    UNDEFINED = 4


# Class that holds the knowledge of the current state and serves as interaction point for all the modules
class Knowledge(object):
    def __init__(self):
        self.status = Status.ARRIVED
        self.memory = {'location': carla.Vector3D(0.0, 0.0, 0.0)}
        self.destination = self.get_location()
        self.status_changed = lambda *_, **__: None
        self.destination_changed = lambda *_, **__: None
        self.data_changed = lambda *_, **__: None

    def set_data_changed_callback(self, callback):
        self.data_changed = callback

    def set_status_changed_callback(self, callback):
        self.status_changed = callback

    def set_destination_changed_callback(self, callback):
        self.destination_changed = callback

    def get_status(self):
        return self.status

    def set_status(self, new_status):
        self.status = new_status

    def get_current_destination(self):
        return self.destination

    def get_speed(self):
        v = self.retrieve_data('velocity')

        return 3.6 * math.sqrt(v.x ** 2 + v.y ** 2 + v.z ** 2)

    def get_target_speed(self):
        return self.retrieve_data('target_speed')

    # Retrieving data from memory
    # !Take note that it is unsafe and does not check whether the given field is in dic
    def retrieve_data(self, data_name):
        return self.memory[data_name]

    # updating status to correct value and making sure that everything is handled properly
    def update_status(self, new_status):
        if (self.status != Status.CRASHED or new_status == Status.HEALING) and self.status != new_status:
            self.set_status(new_status)
            self.status_changed(new_status)

    # Return current location of the vehicle
    def get_location(self):
        return self.retrieve_data('location')

    def arrived_at(self, destination):
        return utils.distance(self.get_location(), destination) < 5.0

    def update_destination(self, new_destination):
        if utils.distance(self.destination, new_destination) > 5.0:
            self.destination = new_destination
            self.destination_changed(new_destination)

    # A function to receive data from monitor
    # TODO: Add callback so that analyser can know when to parse the data
    def update_data(self, data_name, pars):
        self.memory[data_name] = pars
        self.data_changed(data_name)
