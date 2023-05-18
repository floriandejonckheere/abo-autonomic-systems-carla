from collections import deque


class PIDController:
    """Generic PID controller implementation."""

    def __init__(self, K_p, K_i, K_d, size=10):
        self.K_p = K_p
        self.K_i = K_i
        self.K_d = K_d

        # Error signal history
        self.e_T = deque(size * [0.0], size)

    def control(self, reference, output, dt):
        # Compute error signal and add to history
        e_t = reference - output
        self.e_T.append(e_t)

        # Compute proportional term
        p = self.K_p * e_t

        # Compute integral term
        i = self.K_i * sum(self.e_T) * dt

        # Compute derivative term
        d = self.K_d * (self.e_T[-1] - self.e_T[-2]) / dt

        # Return control signal
        return p + i + d
