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

import collections
import math


# Size of history buffer
HISTORY_SIZE = 200

def get_actor_display_name(actor, truncate=250):
    name = ' '.join(actor.type_id.replace('_', '.').title().split('.')[1:])
    return (name[:truncate - 1] + u'\u2026') if len(name) > truncate else name

class Features:
    def __init__(self):
        self.vehicle = None

        self.rotation = None
        self.location = None

        self.state = None

        self.heading = None

        self.speed = None

        self.throttle = None
        self.steer = None
        self.brake = None
        self.hand_brake = None
        self.reverse = None

        self.target_speed = None

        self.throttle_history = collections.deque(HISTORY_SIZE * [0.0], HISTORY_SIZE)
        self.brake_history = collections.deque(HISTORY_SIZE * [0.0], HISTORY_SIZE)
        self.steer_history = collections.deque(HISTORY_SIZE * [0.0], HISTORY_SIZE)
        self.speed_history = collections.deque(HISTORY_SIZE * [0.0], HISTORY_SIZE)
        self.target_speed_history = collections.deque(HISTORY_SIZE * [0.0], HISTORY_SIZE)

    def analyze(self, autopilot):
        vehicle = autopilot.vehicle
        self.vehicle = get_actor_display_name(vehicle, truncate=20)

        transform = vehicle.get_transform()
        self.rotation = transform.rotation
        self.location = transform.location

        self.state = autopilot.knowledge.state_machine.current_state.id

        self.heading = 'N' if abs(self.rotation.yaw) < 89.5 else ''
        self.heading += 'S' if abs(self.rotation.yaw) > 90.5 else ''
        self.heading += 'E' if 179.5 > self.rotation.yaw > 0.5 else ''
        self.heading += 'W' if -0.5 > self.rotation.yaw > -179.5 else ''

        velocity = vehicle.get_velocity()
        self.speed = (3.6 * math.sqrt(velocity.x ** 2 + velocity.y ** 2 + velocity.z ** 2))

        control = vehicle.get_control()
        self.throttle = control.throttle
        self.steer = control.steer
        self.brake = control.brake
        self.hand_brake = control.hand_brake
        self.reverse = control.reverse

        knowledge = autopilot.knowledge
        self.target_speed = knowledge.get_target_speed()

        self.throttle_history.append(self.throttle)
        self.brake_history.append(self.brake)

        # Normalize steer from [-1, 1] to [0, 1]
        self.steer_history.append(self.steer + 1 / 2)

        # Normalize speed from [0, 50] to [0, 1]
        self.speed_history.append(min(self.speed / 50, 50))
        self.target_speed_history.append(min(self.target_speed / 50, 50))
