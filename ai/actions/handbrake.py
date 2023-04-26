from .action import Action


class Handbrake(Action):
    """Brake and apply handbrake"""

    def apply(self, control):
        control.throttle = 0.0

        # FIXME: brake softly based on speed
        control.brake = 1.0
        control.hand_brake = True
