from ai.carla import carla

from .control.controller import Controller


# Executor is responsible for moving the vehicle around
# In this implementation it only needs to match the steering and speed so that we arrive at provided waypoints
class Executor(object):
    def __init__(self, knowledge, vehicle, debug):
        self.vehicle = vehicle
        self.knowledge = knowledge
        self.debug = debug

        # Vehicle controller
        self.controller = Controller(vehicle)

    # Update the executor at some intervals to steer the car in desired direction
    def update(self, dt):
        control = carla.VehicleControl()

        # Apply plan (determine reference points)
        self.knowledge.plan.apply(control)

        # Apply PID control
        self.controller.control(control, dt)

        # Apply control to the vehicle
        self.vehicle.apply_control(control)
