from ai.carla import carla

from collections import deque

import numpy as np
from scipy.interpolate import interp1d

from .graph import Graph
from ..configuration import Configuration


class Navigator:
    """Create and keep track of a route plan based on the current location and destination."""

    def __init__(self, knowledge, world, debug):
        self.knowledge = knowledge
        self.world = world
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
        if self.knowledge.location.distance(self.path[0]) < Configuration.maximum_destination_distance:
            self.visited.append(self.path.popleft())

        if len(self.path) == 0:
            # If there are no more waypoints, we have arrived
            return
        else:
            # Otherwise, we keep driving
            return self.path[0]

    # Total distance of the current route plan
    # TODO: precalculate distances between waypoints when planning
    def distance(self):
        return sum([self.path[i].distance(self.path[i + 1]) for i in range(len(self.path) - 1)])

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

        # # Add source and destination as starting and final waypoints
        topological_path = [location, *topological_path, self.knowledge.destination]

        # If the destination waypoint is too far from the actual destination, interpolate exactly
        exact = destination.transform.location.distance(self.knowledge.destination) > Configuration.maximum_destination_distance

        # Step 2: detailed route plan using local waypoints
        self.enhance(topological_path, exact)

        # Step 3: add final destination
        self.path.append(self.knowledge.destination)

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
        #         self.world.debug.draw_string(self.path[i], str(i), life_time=30, color=carla.Color(255, 0, 0))
        #         self.world.debug.draw_line(self.path[i], self.path[i+1], thickness=0.2, life_time=30, color=carla.Color(255, 0, 0))
        #
        #     # Draw all waypoints in 75m radius (green lines)
        #     for (u, v) in self.graph.graph.edges:
        #         if u.transform.location.distance(self.knowledge.location) < 75.0 or v.transform.location.distance(self.knowledge.location) < 75.0:
        #             self.world.debug.draw_line(u.transform.location, v.transform.location, thickness=0.1, life_time=30, color=carla.Color(0, 255, 0))
        #             self.world.debug.draw_string(u.transform.location, str(u.road_id), life_time=30, color=carla.Color(0, 255, 0))
        #             self.world.debug.draw_string(v.transform.location + carla.Location(z=0.5), str(v.road_id), life_time=30, color=carla.Color(0, 255, 0))

    # Create a detailed path by interpolating the topological path
    def enhance(self, topological_path, exact):
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

        # Create spline interpolator for Cartesian coordinates
        interpolator = interp1d(distances, np.stack((x, y, z), axis=1), kind='slinear', axis=0)

        # Linearly space the distances between interpolated waypoints
        linear_distances = np.arange(0.0, distances[-1], Configuration.waypoint_distance)

        # Interpolate coordinates
        interpolated = interpolator(linear_distances)

        # Create a list of waypoints from the interpolated coordinates
        for i, (xi, yi, zi) in enumerate(interpolated):
            location = carla.Location(x=xi, y=yi, z=zi)

            # Find the closest waypoint location on the map (except for the last 10 waypoints)
            if not (exact and i > len(interpolated) - 10):
                location = self.map.get_waypoint(location).transform.location

            # If the waypoint is close enough to the destination, stop
            # This usually means that the route to the destination is much longer, but following only legal waypoints
            # For example, the locations in milestone two are located a bit before junctions, so the planner
            # would go a block around to reach them using only legal waypoints
            if location.distance(self.knowledge.destination) < Configuration.maximum_destination_distance:
                break

            # Add it to the path
            self.path.append(location)
