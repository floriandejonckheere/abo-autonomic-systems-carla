import math

from ai.state.value import Value


def get_actor_display_name(actor, truncate=250):
    name = ' '.join(actor.type_id.replace('_', '.').title().split('.')[1:])
    return (name[:truncate - 1] + u'\u2026') if len(name) > truncate else name


class Features:
    def __init__(self, size=100):
        self.vehicle = None

        self.rotation = None
        self.location = None

        self.state = None

        self.collision = None
        self.lane_invasion = []

        self.goals = None

        self.heading = None

        self.speed = Value(size=size)
        self.target_speed = Value(size=size)

        self.throttle = Value(size=size)
        self.steer = Value(size=size)
        self.brake = Value(size=size)
        self.hand_brake = None
        self.reverse = None

        self.lidar_image = None
        self.rgb_image = None

        self.depth_image = None

        self.proximity = Value(size=size)
        self.proximity_left = Value(size=size)
        self.proximity_right = Value(size=size)

    def analyze(self, autopilot):
        vehicle = autopilot.vehicle
        knowledge = autopilot.knowledge

        self.vehicle = get_actor_display_name(vehicle, truncate=20)

        transform = vehicle.get_transform()
        self.rotation = transform.rotation
        self.location = transform.location

        self.state = knowledge.state_machine.current_state.id.upper()

        self.collision = knowledge.collision
        self.lane_invasion = knowledge.lane_invasion

        self.goals = knowledge.plan.goals if knowledge.plan else []

        self.heading = 'N' if abs(self.rotation.yaw) < 89.5 else ''
        self.heading += 'S' if abs(self.rotation.yaw) > 90.5 else ''
        self.heading += 'E' if 179.5 > self.rotation.yaw > 0.5 else ''
        self.heading += 'W' if -0.5 > self.rotation.yaw > -179.5 else ''

        self.speed.update(knowledge.speed, ceiling=50)
        self.target_speed.update(knowledge.target_speed, ceiling=50)

        control = vehicle.get_control()
        self.throttle.update(control.throttle)
        self.brake.update(control.brake)

        self.hand_brake = control.hand_brake
        self.reverse = control.reverse

        # Normalize steer from [-1, 1] to [0, 1]
        self.steer.update(control.steer + 1 / 2)

        self.lidar_image = knowledge.lidar_image
        self.rgb_image = knowledge.rgb_image

        self.depth_image = knowledge.depth_image

        self.proximity.update(knowledge.proximity, ceiling=100)

        proximity_left = knowledge.proximity_left.average()
        self.proximity_left.update(0.0 if proximity_left == float('inf') else proximity_left, ceiling=100)

        proximity_right = knowledge.proximity_right.average()
        self.proximity_right.update(0.0 if proximity_right == float('inf') else proximity_right, ceiling=100)
