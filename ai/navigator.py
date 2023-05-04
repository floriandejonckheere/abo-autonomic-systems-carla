from ai.carla import carla

from collections import deque


class Navigator:
    def __init__(self, knowledge, world):
        self.knowledge = knowledge
        self.world = world
        self.map = world.get_map()

        # List of waypoints to follow
        self.path = deque()

        # List of waypoints already visited
        self.visited = deque()

    # Update internal state to make sure that there are waypoints to follow and that we have not arrived yet
    def update(self):
        # If there are no more waypoints, we have arrived
        if len(self.path) == 0:
            return

        # If we are close enough to the next waypoint, remove it from the list
        if self.knowledge.location.distance(self.path[0]) < 5.0:
            self.visited.append(self.path.popleft())

        if len(self.path) == 0:
            # If there are no more waypoints, we have arrived
            return
        else:
            # Otherwise, we keep driving
            return self.path[0]

    # Create a list of waypoints from the current location to the current destination
    def plan(self):
        self.path = deque()
        self.visited = deque()

        # Waypoint on map closest to source location
        waypoint = self.map.get_waypoint(self.knowledge.location)

        distance = float('inf')

        # Draw destination
        self.world.debug.draw_point(self.knowledge.destination, size=0.5, life_time=20, color=carla.Color(0, 255, 0))

        # Iterate over waypoints until we are close enough to the destination,
        # or the distance is increasing again (the vehicle overshot)
        while distance > 5.0 and len(self.path) < 150: # and waypoint.transform.location.distance(destination) < distance:
            # Compute current waypoint distance to destination
            distance = waypoint.transform.location.distance(self.knowledge.destination)

            # Get next (legal) waypoints
            next_waypoints = waypoint.next(2.0)

            # If there is only one next waypoint, then select it
            if len(next_waypoints) == 1:
                waypoint = next_waypoints[0]
            else:
                # If there are multiple next waypoints, then select the one that is closest to destination
                waypoint = min(next_waypoints, key=lambda wp: wp.transform.location.distance(self.knowledge.destination))

            # Add waypoint to path
            self.path.append(waypoint.transform.location)

        # Add destination to path
        self.path.append(self.knowledge.destination)

        # Draw path
        for i in range(0, len(self.path)-2):
            self.world.debug.draw_line(self.path[i], self.path[i+1], thickness=0.2, life_time=20, color=carla.Color(255, 0, 0))
