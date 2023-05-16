import numpy as np

from collections import deque


class Integrator:
    """Smoothen control variables by integration."""

    def __init__(self, vehicle, size=5):
        self.vehicle = vehicle

        # Control variable history
        self.throttle = deque(size * [0.0], size)
        self.steer = deque(size * [0.0], size)

    def integrate(self, control, dt):
        # Convert dt to seconds
        dt /= 1000.0

        self.throttle.append(control.throttle)

        # Integrate control variables
        throttle = sum(self.throttle) * dt

        history = [round(x, 2) for x in self.throttle]
        print(f'{control.throttle:.2f} -> {throttle:.2f} dt={dt:.2f} ({history})')

        control.throttle = throttle
