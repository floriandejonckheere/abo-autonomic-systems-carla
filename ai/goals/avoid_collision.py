from ai.carla import carla

from .goal import Goal

import ai.actions as actions


class AvoidCollision(Goal):
    """Avoid collision with an obstacle"""

    def actions(self):
        if self.knowledge.proximity < 20:
            return [
                # Emergency brake to avoid the obstacle
                actions.EmergencyBrake(),
            ]
        if self.knowledge.proximity_left < 30:
            return [
                # Steer right and brake to avoid the obstacle
                actions.Swerve(0.7),
                actions.Brake(5.0),
            ]
        elif self.knowledge.proximity_right < 30:
            return [
                # Steer left and brake to avoid the obstacle
                actions.Swerve(-0.7),
                actions.Brake(5.0),
            ]
        else:
            return []
