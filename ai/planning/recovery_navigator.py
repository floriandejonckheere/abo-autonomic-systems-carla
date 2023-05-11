from ai.carla import carla

from .navigator import Navigator


class RecoveryNavigator(Navigator):
    """Create and keep track of a recovery plan based on the current location and location history."""

    # Update internal state to make sure that there are waypoints to follow and that we have not recovered yet
    def update(self):
        # If there are no more waypoints, we have arrived
        if len(self.path) == 0:
            print(f'arrived')
            return

        # If we are close enough to the next waypoint, remove it from the list
        if self.knowledge.location.distance(self.path[0]) < 2.5:
            self.path.popleft()

        if len(self.path) == 0:
            # If there are no more waypoints, we have recovered
            return
        else:
            # Otherwise, we keep driving
            return self.path[0]

    # Create a list of waypoints to follow based on the location history
    def plan(self):
        # Recovery path is simply location history in reverse order
        self.path = self.knowledge.location_history.copy()
        self.path.reverse()

        if self.debug:
            # Draw last location and recovery destination
            self.world.debug.draw_string(self.path[0], 'Location', life_time=10, color=carla.Color(255, 255, 0))
            self.world.debug.draw_string(self.path[-1], 'Recovery', life_time=10, color=carla.Color(255, 255, 0))

            # Draw waypoints
            for waypoint in self.path:
                self.world.debug.draw_point(waypoint, size=0.2, life_time=10, color=carla.Color(255, 0, 0))

            # Draw planned route (blue lines)
            for i in range(0, len(self.path)-1):
                self.world.debug.draw_line(self.path[i], self.path[i+1], thickness=0.2, life_time=10, color=carla.Color(0, 0, 255))
