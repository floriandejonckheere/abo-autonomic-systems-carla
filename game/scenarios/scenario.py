from collections import deque

from ai.carla import carla


class Scenario:
    """Base class for all scenarios."""

    WAYPOINTS = []

    def __init__(self, world):
        self.world = world
        self.actors = []

        self.waypoints = deque([carla.Transform(location=wp) for wp in self.WAYPOINTS])

        # Use nearby CARLA spawnpoint
        self.use_spawnpoint = True

    def setup(self):
        pass

    def destroy(self):
        for actor in self.actors:
            actor.is_alive and actor.destroy()

    def next_waypoint(self):
        try:
            return self.waypoints.popleft()
        except IndexError:
            return None
