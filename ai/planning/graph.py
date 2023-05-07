from ai.carla import carla

import networkx as nx

from .node import Node


class Graph:
    """Weighted directed graph of the topological waypoints on the map."""

    def __init__(self, topology):
        self.topology = topology
        self.graph = nx.DiGraph()

        # Dictionary of parallel edges based on road id
        parallel = {}

        for (u, v) in topology:
            # Wrap waypoints in Node objects
            u = Node(u)
            v = Node(v)

            # Add edge to graph
            self.graph.add_edge(u, v, weight=u.transform.location.distance(v.transform.location))

            # Register parallel edges
            if not parallel.get((u.road_id, v.road_id)):
                parallel[(u.road_id, v.road_id)] = []

            parallel[(u.road_id, v.road_id)].append((u, v))

        # Add lane changes for parallel edges
        for edges in parallel.values():
            if len(edges) == 1:
                continue

            # Assume there are only two parallel edges (maximum two lanes per road)
            u, v = edges[0]
            u_, v_ = edges[1]

            # Add lane change edges (if allowed)
            if not u.lane_change.name == 'None' and not u.is_intersection:
                self.graph.add_edge(u, v_, weight=u.transform.location.distance(v_.transform.location))

            if not u_.lane_change.name == 'None' and not u_.is_intersection:
                self.graph.add_edge(u_, v, weight=u_.transform.location.distance(v.transform.location))

        print(f'Nodes={len(self.graph.nodes)} Edges={len(self.graph.edges)} Waypoints={len(topology)}')

    # Return the shortest path between two waypoints in the graph
    def shortest_path(self, source, destination):
        # Find the closest topological waypoints to the source and destination (same road and lane)
        source = next(v for (u, v) in self.topology if v.road_id == source.road_id and v.lane_id == source.lane_id)
        destination = next(u for (u, v) in self.topology if v.road_id == destination.road_id and v.lane_id == destination.lane_id)

        # Wrap waypoints in Node objects
        source = Node(source)
        destination = Node(destination)

        # Find the shortest path between the source and destination
        return nx.dijkstra_path(self.graph, source=source, target=destination)
