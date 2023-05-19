from ai.carla import carla

from .goal import Goal

import ai.actions as actions


class Wait(Goal):
    """Wait at traffic lights."""

    def actions(self):
        # Don't wait if there is no traffic light or if the traffic light is green
        if not self.knowledge.is_at_traffic_light or self.knowledge.traffic_light.state == carla.TrafficLightState.Green:
            return []

        return [
            # Brake to wait at the traffic light
            actions.Brake(self.knowledge.location.distance(self.knowledge.traffic_light.get_transform().location)),
        ]
