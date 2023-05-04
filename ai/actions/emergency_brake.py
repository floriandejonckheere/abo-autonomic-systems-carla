from .action import Action


class EmergencyBrake(Action):
    """Apply emergency brake"""

    def apply(self, control):
        # Set throttle and brake
        control.throttle = 0.0
        control.brake = 1.0
        control.hand_brake = True  # Not usually a good idea in emergencies, but we need the breaking power
