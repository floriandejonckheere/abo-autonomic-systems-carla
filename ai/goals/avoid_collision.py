from .goal import Goal

import ai.actions as actions


class AvoidCollision(Goal):
    """Avoid collision with an obstacle"""

    def actions(self):
        if self.knowledge.obstacle:
            return [
                # Emergency brake to avoid the obstacle in front
                actions.EmergencyBrake(),
            ]
        if self.knowledge.obstacle_left:
            return [
                # Steer right and brake to avoid the obstacle on the left
                actions.Swerve(actions.Swerve.Right, self.knowledge.proximity_left),
                actions.Brake(3.0),
            ]
        elif self.knowledge.obstacle_right:
            return [
                # Steer left and brake to avoid the obstacle on the right
                actions.Swerve(actions.Swerve.Left, self.knowledge.proximity_right),
                actions.Brake(3.0),
            ]
        else:
            return [
                # No obstacle in sight, brake until healing timeout expires
                actions.Brake(1.0),
            ]
