from ai.carla import carla

from .goal import Goal

import ai.actions as actions


class Swerve(Goal):
    """Swerve to avoid an obstacle."""

    def actions(self):
        if self.knowledge.proximity_left < 30:
            return [
                # Steer right to avoid the obstacle
                actions.Swerve(0.7),
                actions.EmergencyBrake(),
            ]
        elif self.knowledge.proximity_right < 30:
            return [
                # Steer left to avoid the obstacle
                actions.Swerve(-0.7),
                actions.EmergencyBrake(),
            ]
        else:
            return []
