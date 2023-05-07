from .pid_controller import PIDController

class Controller:
    """Control multiple continuous variables using PID control."""

    def __init__(self, vehicle):
        self.vehicle = vehicle

        # Instatiate PID controllers for continuous variables
        self.throttle_controller = PIDController(K_p=1.0, K_i=0.0, K_d=0.0)

    def control(self, control, dt):
        # Convert dt to seconds
        dt /= 1000.0

        # Apply PID control
        control.throttle = self.throttle_controller.control(control.throttle, self.vehicle.get_control().throttle, dt)
