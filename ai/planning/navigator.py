from ai.carla import carla

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
        # for (u, v) in self.graph.graph.edges:
        #     self.world.debug.draw_line(u.transform.location, v.transform.location, thickness=0.1, life_time=30, color=carla.Color(0, 255, 0))
        #     self.world.debug.draw_string(u.transform.location, str(u.road_id), life_time=30, color=carla.Color(0, 255, 0))
        #     self.world.debug.draw_string(v.transform.location + carla.Location(z=0.5), str(v.road_id), life_time=30, color=carla.Color(0, 255, 0))

        for waypoint in topological_path:
            self.path.append(waypoint.transform.location)

        # Add destination as final waypoint
        self.path.append(self.knowledge.destination)

        # Draw full path
        for i in range(1, len(self.path)):
            self.world.debug.draw_line(self.path[i-1], self.path[i], thickness=0.2, life_time=30, color=carla.Color(255, 0, 0))

        return

        # FIXME: let detailed route plan use lane changes

        ## Step 2: detailed route plan using local waypoints

        # For each segment in the topological path, compute a detailed route
        for segment_start, segment_end in zip(topological_path, topological_path[1:]):
            # Compute a detailed route for the current lane and the other lane (if it exists),
            # and select the one that ends up closest to the destination
            waypoints = [segment_start, segment_start.get_left_lane(), segment_start.get_right_lane()]
            waypoints = [wp for wp in waypoints if wp is not None]

            print(f'{segment_start.road_id} -> {segment_end.road_id}, {segment_start.lane_id} -> {segment_end.lane_id}')

            # Final segment path
            segment_path = None

            for candidate in waypoints:
                distance = float('inf')
                waypoint = candidate

                # Initialize empty path for candidate
                path = []

                # Iterate over waypoints until we are close enough to the destination,
                # or the path is longer than 300 waypoints (~600m)
                while distance > 5.0:
                    if len(path) > 100:
                        # If the path is getting too long, then stop
                        break

                    # Compute current waypoint distance to segment end
                    distance = waypoint.transform.location.distance(segment_end.transform.location)

                    # Get next (legal) waypoints
                    next_waypoints = waypoint.next(2.0)

                    if len(next_waypoints) == 0:
                        # If there are no next waypoints, then stop
                        break
                    elif len(next_waypoints) == 1:
                        # If there is only one next waypoint, then select it
                        waypoint = next_waypoints[0]
                    else:
                        # If there are multiple next waypoints, then select the one that is closest to destination
                        waypoint = min(next_waypoints, key=lambda wp: wp.transform.location.distance(segment_end.transform.location))

                    # Add waypoint to candidate path
                    path.append(waypoint.transform.location)

                # Candidate satisfies the distance requirement, so it can be used
                segment_path = path

            if segment_path is None:
                raise Exception(f'Could not find path from {segment_start} to {segment_end}')

            # Add segment path to full path
            self.path.extend(segment_path)

        # Add destination as final waypoint
        self.path.append(self.knowledge.destination)

        # Draw full path
        for i in range(0, len(self.path)-1):
            self.world.debug.draw_line(self.path[i], self.path[i+1], thickness=0.2, life_time=30, color=carla.Color(255, 0, 0))