import networkx as nx

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

        # Create graph of the map topology
        self.topology = self.map.get_topology()
        self.graph = nx.DiGraph()

        # Build graph
        self.location_to_node_id = {}
        self.node_id_to_waypoint = {}

        i = 0

        for (u, v) in self.topology:
            node_id = (u.transform.location.x, u.transform.location.y)
            if not self.location_to_node_id.get(node_id):
                self.location_to_node_id[node_id] = i
                self.node_id_to_waypoint[i] = u
                i += 1

            node_id = (v.transform.location.x, v.transform.location.y)
            if not self.location_to_node_id.get(node_id):
                self.location_to_node_id[node_id] = i
                self.node_id_to_waypoint[i] = v
                i += 1

            self.graph.add_edge(
                self.location_to_node_id[(u.transform.location.x, u.transform.location.y)],
                self.location_to_node_id[(v.transform.location.x, v.transform.location.y)],
            )

        # self.graph.add_edges_from([(u.transform.location, v.transform.location) for (u, v) in self.topology])

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
        # Topology waypoint closest to source (end of road waypoint on same road as source, in the same lane)
        source_wp = next(v for (u, v) in self.topology if v.road_id == source.road_id and v.lane_id == source.lane_id)

        # Topology waypoint closest to destination (end of road waypoint on same road as destination, in the same lane)
        destination_wp = next(v for (u, v) in self.topology if v.road_id == destination.road_id and v.lane_id == destination.lane_id)

        source_id = self.location_to_node_id[(source_wp.transform.location.x, source_wp.transform.location.y)]
        destination_id = self.location_to_node_id[(destination_wp.transform.location.x, destination_wp.transform.location.y)]

        print(source_id, destination_id)

        path = nx.shortest_path(self.graph, source=source_id, target=destination_id)

        print(path)

        for node_id in path:
            self.path.append(self.node_id_to_waypoint[node_id].transform.location)

        # Add destination
        self.path.append(destination.transform.location)

        # Draw path
        for i in range(0, len(self.path)-1):
            self.world.debug.draw_line(self.path[i], self.path[i+1], thickness=0.2, life_time=60, color=carla.Color(255, 0, 0))

        # Draw source
        self.world.debug.draw_string(self.knowledge.location, 'S', life_time=20, color=carla.Color(255, 255, 0))
        self.world.debug.draw_string(source.transform.location, str(source.road_id), life_time=20, color=carla.Color(255, 255, 0))

        # Draw destination
        self.world.debug.draw_string(self.knowledge.destination, 'D', life_time=20, color=carla.Color(0, 255, 0))
        self.world.debug.draw_string(destination.transform.location + carla.Location(z=1), str(destination.road_id), life_time=20, color=carla.Color(0, 255, 0))

        # Draw all waypoints
        for (u, v) in self.topology:
            self.world.debug.draw_line(u.transform.location, v.transform.location, thickness=0.1, life_time=20, color=carla.Color(0, 255, 0))
        #     self.world.debug.draw_string(u.transform.location, str(u.road_id), life_time=20, color=carla.Color(255, 0, 0))
        #     self.world.debug.draw_string(v.transform.location + carla.Location(z=0.5), str(v.road_id), life_time=20, color=carla.Color(255, 0, 0))

        for node_id in self.graph.nodes:
            wp = self.node_id_to_waypoint[node_id]
            self.world.debug.draw_string(wp.transform.location, str(node_id), life_time=20, color=carla.Color(255, 0, 0))

        ## Step 2: detailed route plan using local waypoints
        distance = float('inf')
        waypoint = source



        return



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
