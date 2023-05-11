from .goal import Goal

import ai.actions as actions


class Stop(Goal):
    """Stop the vehicle"""

    def actions(self):
        return [
            # Brake
            actions.Brake(3.0),

            # Apply handbrake when stopped
            actions.Handbrake(self.knowledge.speed()),
        ]
