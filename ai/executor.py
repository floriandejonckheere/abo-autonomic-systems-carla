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
        # TODO: Take into account that exiting the crash site could also be done in reverse, so there might need to be
        #  additional data passed between planner and executor, or there needs to be some way to tell this that it is ok
        #  to drive in reverse during healing and crashed states. An example is additional_vars, that could be a list with
        #  parameters that can tell us which things we can do (for example going in reverse)
        control = carla.VehicleControl()

        # Apply plan (determine reference points)
        self.knowledge.plan.apply(control)

        # Apply PID control
        self.controller.control(control, dt)

        # Apply control to the vehicle
        self.vehicle.apply_control(control)
