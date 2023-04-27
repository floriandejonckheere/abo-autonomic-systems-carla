from .action import Action


class Handbrake(Action):
    """Apply handbrake"""

    def __init__(self, speed):
        self.speed = speed

    def apply(self, control):
        control.throttle = 0.0

        # Apply handbrake if speed is low enough
        control.hand_brake = True if self.speed < 5.0 else False
