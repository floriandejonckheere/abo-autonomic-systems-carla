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


# Executor is responsible for moving the vehicle around
# In this implementation it only needs to match the steering and speed so that we arrive at provided waypoints
# BONUS TODO: implement different speed limits so that planner would also provide speed target speed in addition to
#  direction
class Executor(object):
    def __init__(self, knowledge, vehicle):
        self.vehicle = vehicle
        self.knowledge = knowledge

    # Update the executor at some intervals to steer the car in desired direction
    def update(self):
        # TODO: steer in the direction of destination and throttle or brake depending on how close we are to destination
        # TODO: Take into account that exiting the crash site could also be done in reverse, so there might need to be
        #  additional data passed between planner and executor, or there needs to be some way to tell this that it is ok
        #  to drive in reverse during healing and crashed states. An example is additional_vars, that could be a list with
        #  parameters that can tell us which things we can do (for example going in reverse)
        control = carla.VehicleControl()

        # Execute action queue in-order
        for action in self.knowledge.queue:
            action.apply(control)

        # Clear action queue
        self.knowledge.queue.clear()

        # Apply control to vehicle
        self.vehicle.apply_control(control)
