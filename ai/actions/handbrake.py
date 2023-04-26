from .action import Action

class Handbrake(Action):
    def apply(self, control):
        control.throttle = 0.0

        # FIXME: brake softly based on speed
        control.brake = 1.0
        control.hand_brake = True
