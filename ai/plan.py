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


class Plan:
    """Execution plan created by the planner, composed of high-level goals and low-level actions"""

    def __init__(self):
        self.goals = []

    def execute(self, vehicle):
        control = carla.VehicleControl()

        # For each high-level goal, apply its actions to the vehicle control
        for action in self.actions():
            action.apply(control)

        # Apply control to the vehicle
        vehicle.apply_control(control)

    def actions(self):
        return [action for goal in self.goals for action in goal.actions()]
