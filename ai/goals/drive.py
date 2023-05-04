from ai.carla import carla

from .goal import Goal

import ai.actions as actions


class Drive(Goal):
    """Drive towards the next waypoint"""

    def actions(self):
        # Target location vector (relative to source)
        target = carla.Location(
            self.knowledge.waypoint.x - self.knowledge.location.x,
            self.knowledge.waypoint.y - self.knowledge.location.y,
        )

        return [
            # Accelerate towards a waypoint
            actions.Accelerate(self.knowledge.location.distance(self.knowledge.waypoint)),
            actions.Limit(self.knowledge.speed(), self.knowledge.target_speed),

            # Steer towards the next waypoint
            actions.Steer(self.knowledge.rotation.get_forward_vector(), target),

            # Stop-and-go in dense traffic
            actions.Cruise(self.knowledge.proximity, self.knowledge.speed()),
        ]
