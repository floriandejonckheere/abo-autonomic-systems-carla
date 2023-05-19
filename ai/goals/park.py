from .goal import Goal

import ai.actions as actions


class Park(Goal):
    """Park the vehicle"""

    def actions(self):
        return [
            # Brake gently
            actions.Brake(self.knowledge.location.distance(self.knowledge.waypoint)),

            # Apply handbrake when stopped
            actions.Handbrake(self.knowledge.speed),
        ]
