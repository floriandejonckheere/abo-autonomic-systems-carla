from ai.carla import carla

from .goal import Goal

import ai.actions as actions


class AvoidCollision(Goal):
    """Avoid collision with an obstacle"""

    def actions(self):
        if self.knowledge.obstacle:
            return [
                # Emergency brake to avoid the obstacle
                actions.EmergencyBrake(),
            ]
        if self.knowledge.obstacle_left:
            return [
                # Steer right and brake to avoid the obstacle
                actions.Swerve(0.7),
                actions.Brake(3.0),
            ]
        elif self.knowledge.obstacle_right:
            return [
                # Steer left and brake to avoid the obstacle
                actions.Swerve(-0.7),
                actions.Brake(3.0),
            ]
        else:
            return [
                # No obstacle in sight, wait until healing timeout expires
                actions.Brake(0.0),
            ]
