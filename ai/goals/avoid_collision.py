from .goal import Goal

import ai.actions as actions


class AvoidCollision(Goal):
    """Avoid collision with an obstacle."""

    def __init__(self, knowledge):
        super().__init__(knowledge, emergency=True)

    def actions(self):
        if self.knowledge.obstacle:
            return [
                # Emergency brake to avoid the obstacle in front
                actions.EmergencyBrake(),
            ]
        if self.knowledge.obstacle_left and self.knowledge.speed > 1.0:
            return [
                # Steer right and brake to avoid the obstacle on the left
                actions.Swerve(actions.Swerve.Right, self.knowledge.proximity_left.average()),
                actions.Brake(3.0),
            ]
        elif self.knowledge.obstacle_right and self.knowledge.speed > 1.0:
            return [
                # Steer left and brake to avoid the obstacle on the right
                actions.Swerve(actions.Swerve.Left, self.knowledge.proximity_right.average()),
                actions.Brake(3.0),
            ]
        else:
            return [
                # No obstacle in sight, brake until healing timeout expires
                actions.Brake(1.0),
            ]
