from ai.carla import carla


class Plan:
    """Execution plan created by the planner, composed of high-level goals and low-level actions"""

    def __init__(self):
        self.goals = []

    def execute(self, vehicle):
        control = carla.VehicleControl()

        # For each high-level goal, apply its actions to the vehicle control
        for goal in self.goals:
            for action in goal.actions():
                action.apply(control)

        # Apply control to the vehicle
        vehicle.apply_control(control)
