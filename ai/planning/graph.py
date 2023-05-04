import networkx as nx


class Graph:
    """Topological waypoint graph of the map."""

    def __init__(self, topology):
        self.topology = topology

        self.graph = nx.DiGraph()

        self.location_to_node_id = {}
        self.node_id_to_waypoint = {}

        i = 0

        for (u, v) in topology:
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

    # Return the topology waypoint closest to the given waypoint (on same road and lane)
    def topological_waypoint_for(self, waypoint):
        return next(v for (u, v) in self.topology if v.road_id == waypoint.road_id and v.lane_id == waypoint.lane_id)

    # Return the shortest path between two waypoints in the graph
    def shortest_path(self, source, destination):
        source_id = self.location_to_node_id[(source.transform.location.x, source.transform.location.y)]
        destination_id = self.location_to_node_id[(destination.transform.location.x, destination.transform.location.y)]

        path = nx.shortest_path(self.graph, source=source_id, target=destination_id)

        return [self.node_id_to_waypoint[node_id] for node_id in path]
