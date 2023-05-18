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
        else:
            return [
                # No obstacle in sight, brake until healing timeout expires
                actions.Brake(1.0),
            ]
