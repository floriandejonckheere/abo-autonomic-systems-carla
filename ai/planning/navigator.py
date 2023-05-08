from ai.carla import carla

from collections import deque

from .graph import Graph


class Navigator:
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
        topological_path = self.graph.shortest_path(source, destination)

        # Step 2: detailed route plan using local waypoints
        # FIXME: remove detailed switch once navigation bug is fixed
        if self.detailed:
            self.enhance(topological_path)
        else:
            for waypoint in topological_path:
                self.path.append(waypoint.transform.location)

        # Add destination as final waypoint
        self.path.append(self.knowledge.destination)

        if self.debug:
            # Print waypoints
            # for waypoint in self.path:
            #     print(waypoint)

            # Draw source and destination
            self.world.debug.draw_string(self.knowledge.location, 'Source', life_time=20, color=carla.Color(255, 255, 0))
            self.world.debug.draw_string(self.knowledge.destination, 'Destination', life_time=20, color=carla.Color(0, 255, 0))

            # Draw planned route (red lines)
            for i in range(0, len(self.path)-1):
                self.world.debug.draw_line(self.path[i], self.path[i+1], thickness=0.2, life_time=30, color=carla.Color(255, 0, 0))

            # Draw all waypoints in 75m radius (green lines)
            for (u, v) in self.graph.graph.edges:
                if u.transform.location.distance(self.knowledge.location) < 75.0 or v.transform.location.distance(self.knowledge.location) < 75.0:
                    self.world.debug.draw_line(u.transform.location, v.transform.location, thickness=0.1, life_time=30, color=carla.Color(0, 255, 0))
                    self.world.debug.draw_string(u.transform.location, str(u.road_id), life_time=30, color=carla.Color(0, 255, 0))
                    self.world.debug.draw_string(v.transform.location + carla.Location(z=0.5), str(v.road_id), life_time=30, color=carla.Color(0, 255, 0))

    def enhance(self, topological_path):
        # For each segment in the topological path, calculate a detailed route using a recursive backtracking algorithm
        for segment_start, segment_end in zip(topological_path[:-1], topological_path[1:]):
            waypoint = segment_start
            distance = float('inf')

            # Iterate over waypoints until we are close enough to the destination,
            # or the path is longer than 150 waypoints (~300m)
            while distance > 5.0:
                if len(self.path) > 150:
                    raise Exception('Could not find a path to the waypoint in less than 150 steps')

                # Compute current waypoint distance to destination
                distance = waypoint.transform.location.distance(segment_end.transform.location)

                # Get next (legal) waypoints
                next_waypoints = waypoint.next(2.0)

                # If there is only one next waypoint, then select it
                if len(next_waypoints) == 1:
                    waypoint = next_waypoints[0]
                else:
                    # If there are multiple next waypoints, then select the one that is closest to destination
                    waypoint = min(next_waypoints, key=lambda wp: wp.transform.location.distance(segment_end.transform.location))

                # Add waypoint to path
                self.path.append(waypoint.transform.location)
