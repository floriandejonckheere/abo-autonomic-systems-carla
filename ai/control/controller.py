import numpy as np

from .pid_controller import PIDController


class Controller:
    """Control multiple continuous variables using PID control."""

    def __init__(self, vehicle):
        self.vehicle = vehicle

        # Instantiate PID controllers for continuous variables
        self.throttle_controller = PIDController(K_p=0.2, K_i=2.5, K_d=0.0)
        self.brake_controller = PIDController(K_p=0.35, K_i=2.0, K_d=0.0)

        # Steering controller needs less history to prevent oscillations after turns
        self.steer_controller = PIDController(K_p=0.5, K_i=1.5, K_d=0.01, size=5)

    def control(self, control, dt):
        # Convert dt to seconds
        dt /= 1000.0

        # Apply PID control
        control.throttle = np.clip(self.throttle_controller.control(control.throttle, self.vehicle.get_control().throttle, dt), 0.0, 1.0)
        control.brake = np.clip(self.brake_controller.control(control.brake, self.vehicle.get_control().brake, dt), 0.0, 1.0)
        control.steer = np.clip(self.steer_controller.control(control.steer, self.vehicle.get_control().steer, dt), -0.7, 0.7)
