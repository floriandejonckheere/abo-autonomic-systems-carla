from .action import Action


class Swerve(Action):
    """Swerve to avoid an obstacle"""

    def __init__(self, direction):
        self.direction = direction

    def apply(self, control):
        # Set steering
        control.steer = self.direction
