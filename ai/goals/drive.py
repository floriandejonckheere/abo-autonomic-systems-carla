from ai.carla import carla

from .goal import Goal

import ai.actions as actions


class Drive(Goal):
    """Drive towards the next waypoint."""

    def actions(self):
        # Target location vector (relative to source)
        target = carla.Location(
            self.knowledge.waypoint.x - self.knowledge.location.x,
            self.knowledge.waypoint.y - self.knowledge.location.y,
        )

        return [
            # Put the vehicle in forward gear
            actions.Shift(reverse=False),

            # Accelerate towards the end of the waypoint path
            actions.Accelerate(self.knowledge.distance, self.knowledge.speed, self.knowledge.target_speed),

            # Steer towards a waypoint
            actions.Steer(self.knowledge.rotation.get_forward_vector(), target),

            # Stop-and-go in dense traffic
            actions.Cruise(self.knowledge.proximity, self.knowledge.speed),
        ]
