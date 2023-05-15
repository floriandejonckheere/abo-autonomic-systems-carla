from ai.carla import carla

from collections import deque

import numpy as np
from scipy.interpolate import interp1d

from .graph import Graph


class Navigator:
    """Create and keep track of a route plan based on the current location and destination."""

    def __init__(self, knowledge, world, debug, detailed=True):
        self.knowledge = knowledge
        self.world = world
        self.detailed = detailed
        self.debug = debug

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
        # Determine starting location
        if len(self.visited) == 0:
            # If we have not visited any waypoints yet, start from waypoint closest to current location
            location = self.knowledge.location
        else:
            # Otherwise, start from the last visited waypoint
            location = self.visited.pop()

        # Clear path and visited lists
        self.path.clear()
        self.visited.clear()

        # Waypoint on map closest to source location
        source = self.map.get_waypoint(location)

        # Waypoint on map closest to destination location
        destination = self.map.get_waypoint(self.knowledge.destination)

        # Step 1: global route plan using topology waypoints
        topological_path = [wp.transform.location for wp in self.graph.shortest_path(source, destination)]

        # # Add destination as final waypoint
        topological_path.append(self.knowledge.destination)

        # Step 2: detailed route plan using local waypoints
        # FIXME: remove detailed switch once navigation bug is fixed
        if self.detailed:
            self.enhance(topological_path)
        else:
            for waypoint in topological_path:
                self.path.append(waypoint.transform.location)

        # if self.debug:
        #     # Print waypoints
        #     # for waypoint in self.path:
        #     #     print(waypoint)
        #
        #     # Draw source and destination
        #     self.world.debug.draw_string(self.knowledge.location, 'Source', life_time=20, color=carla.Color(255, 255, 0))
        #     self.world.debug.draw_string(self.knowledge.destination, 'Destination', life_time=20, color=carla.Color(0, 255, 0))
        #
        #     # Draw planned route (red lines)
        #     for i in range(0, len(self.path)-1):
        #         self.world.debug.draw_line(self.path[i], self.path[i+1], thickness=0.2, life_time=30, color=carla.Color(255, 0, 0))
        #
        #     # Draw all waypoints in 75m radius (green lines)
        #     for (u, v) in self.graph.graph.edges:
        #         if u.transform.location.distance(self.knowledge.location) < 75.0 or v.transform.location.distance(self.knowledge.location) < 75.0:
        #             self.world.debug.draw_line(u.transform.location, v.transform.location, thickness=0.1, life_time=30, color=carla.Color(0, 255, 0))
        #             self.world.debug.draw_string(u.transform.location, str(u.road_id), life_time=30, color=carla.Color(0, 255, 0))
        #             self.world.debug.draw_string(v.transform.location + carla.Location(z=0.5), str(v.road_id), life_time=30, color=carla.Color(0, 255, 0))

    # Create a detailed path by interpolating the topological path with a cubic spline
    def enhance(self, topological_path):
        x = [waypoint.x for waypoint in topological_path]
        y = [waypoint.y for waypoint in topological_path]
        z = [waypoint.z for waypoint in topological_path]

        # List of distances between waypoints
        distances = [0.0]

        # Calculate Euclidean distance between subsequent waypoints
        for start, end in zip(topological_path[:-1], topological_path[1:]):
            distances.append(start.distance(end))

        # Cumulative sum of distances
        distances = np.cumsum(distances)

        # Create cubic spline interpolator for Cartesian coordinates
        interpolator = interp1d(distances, np.stack((x, y, z), axis=1), kind='cubic', axis=0)

        # Linearly space the distances between interpolated waypoints (2 meter)
        linear_distances = np.arange(0.0, distances[-1], 2.0)

        # Interpolate coordinates
        interpolated = interpolator(linear_distances)

        # Create a list of waypoints from the interpolated coordinates
        for xi, yi, zi in interpolated:
            location = carla.Location(x=xi, y=yi, z=zi)

            # Find the closest waypoint on the map
            waypoint = self.map.get_waypoint(location)

            # Add it to the path
            self.path.append(waypoint.transform.location)
