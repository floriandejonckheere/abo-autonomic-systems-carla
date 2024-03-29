from ai.carla import carla

from .goal import Goal

import ai.actions as actions


class Reverse(Goal):
    """Reverse towards the previous waypoint."""

    def actions(self):
        # Target location vector (relative to source)
        target = carla.Location(
            self.knowledge.waypoint.x - self.knowledge.location.x,
            self.knowledge.waypoint.y - self.knowledge.location.y,
        )

        return [
            # Put the vehicle in reverse gear
            actions.Shift(reverse=True),

            # Accelerate (gently) towards the destination
            actions.Accelerate(self.knowledge.distance, self.knowledge.speed, self.knowledge.target_speed),

            # Steer (gently) towards a waypoint
            actions.Steer(self.knowledge.rotation.get_forward_vector(), target, bounds=(-0.3, 0.3)),
        ]
