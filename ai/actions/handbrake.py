from .action import Action


class Handbrake(Action):
    """Apply handbrake if speed is low enough."""

    def __init__(self, speed):
        self.speed = speed

    def apply(self, control):
        control.throttle = 0.0

        # Release brake and apply handbrake if speed is low enough
        if self.speed < 5.0:
            control.brake = 0.0
            control.hand_brake = True
        else:
            control.hand_brake = False
