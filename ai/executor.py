from ai.carla import carla

from .control.controller import Controller


class Executor(object):
    """Executor is responsible for moving the vehicle around using the execution plan."""

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

        # Apply PID control (if none of the goals require emergency actions)
        if not any([goal.emergency for goal in self.knowledge.plan.goals]):
            self.controller.control(control, dt)

        # Apply control to the vehicle
        self.vehicle.apply_control(control)
