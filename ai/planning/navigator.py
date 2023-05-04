from ai.carla import carla

import numpy as np

from collections import deque

from .graph import Graph


class Navigator:
    def __init__(self, knowledge, world):
        self.knowledge = knowledge
        self.world = world
        self.map = world.get_map()

        # List of waypoints to follow
        self.path = deque()

        # List of waypoints already visited
        self.visited = deque()

        # Create graph of the map topology
        self.graph = Graph(self.map.get_topology())

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
        source = self.map.get_waypoint(self.knowledge.location)

        # Waypoint on map closest to destination location
        destination = self.map.get_waypoint(self.knowledge.destination)

        ## Step 1: global route plan using topology waypoints
        topological_path = self.graph.shortest_path(source, destination)

        # Add destination as final waypoint
        topological_path.append(destination)

        # Draw path
        for i in range(0, len(self.path)-1):
            self.world.debug.draw_line(self.path[i], self.path[i+1], thickness=0.2, life_time=20, color=carla.Color(255, 0, 0))

        # Draw source
        self.world.debug.draw_string(self.knowledge.location, 'S', life_time=20, color=carla.Color(255, 255, 0))
        self.world.debug.draw_string(source.transform.location, str(source.road_id), life_time=20, color=carla.Color(255, 255, 0))

        # Draw destination
        self.world.debug.draw_string(self.knowledge.destination, 'D', life_time=20, color=carla.Color(0, 255, 0))
        self.world.debug.draw_string(destination.transform.location + carla.Location(z=1), str(destination.road_id), life_time=20, color=carla.Color(0, 255, 0))

        # Draw all waypoints
        for (u, v) in self.graph.topology:
            self.world.debug.draw_line(u.transform.location, v.transform.location, thickness=0.1, life_time=20, color=carla.Color(0, 255, 0))

        for node_id, wp in self.graph.node_id_to_waypoint.items():
            self.world.debug.draw_string(wp.transform.location, str(node_id), life_time=20, color=carla.Color(255, 0, 0))

        ## Step 2: detailed route plan using local waypoints

        # For each pair of waypoints in the topological path, compute a detailed route
        for first, second in zip(topological_path, topological_path[1:]):
            distance = float('inf')
            waypoint = first

            # Iterate over waypoints until we are close enough to the destination,
            # the path is longer than 300 waypoints,
            # or the distance is increasing again (the vehicle overshot)
            while distance > 5.0 and len(self.path) < 300 and waypoint.transform.location.distance(second.transform.location) < distance:
                # Compute current waypoint distance to destination
                distance = waypoint.transform.location.distance(second.transform.location)

                # Get next (legal) waypoints
                next_waypoints = waypoint.next(2.0)

                # If there is only one next waypoint, then select it
                if len(next_waypoints) == 1:
                    waypoint = next_waypoints[0]
                else:
                    # If there are multiple next waypoints, then select the one that is closest to destination
                    waypoint = min(next_waypoints, key=lambda wp: wp.transform.location.distance(second.transform.location))

                # Add waypoint to path
                self.path.append(waypoint.transform.location)

        # Draw full path
        for i in range(0, len(self.path)-2):
            self.world.debug.draw_line(self.path[i], self.path[i+1], thickness=0.2, life_time=20, color=carla.Color(255, 0, 0))
