from .action import Action
from ..controllers.fuzzy import Fuzzy


class Drive(Action):
    def __init__(self, knowledge):
        super().__init__(knowledge)

        self.controller = Fuzzy()

    def apply(self, control):
        # Get current and target speed
        speed = self.knowledge.speed()
        target_speed = self.knowledge.target_speed

        # Distance and angle to waypoint
        distance = self.knowledge.distance_to_waypoint()
        angle = self.knowledge.angle_to_waypoint()

        # Update fuzzy controller
        self.controller.update(distance, speed, target_speed, angle)

        # Set throttle and brake
        control.throttle = self.controller.get_throttle()
        control.brake = self.controller.get_brake()
        control.hand_brake = False

        # Set steering
        control.steer = self.controller.get_steer()
