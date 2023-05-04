from ai.carla import carla

import networkx as nx

from .node import Node


class Graph:
    """Topological waypoint graph of the map."""

    def __init__(self, topology):
        self.topology = topology
        self.graph = nx.DiGraph()

        for (u, v) in topology:
            # Wrap waypoints in Node objects
            u = Node(u)
            v = Node(v)

            self.graph.add_edge(u, v)

        print(f'Nodes={len(self.graph.nodes)} Edges={len(self.graph.edges)} Waypoints={len(topology)}')

    # Return the shortest path between two waypoints in the graph
    def shortest_path(self, source, destination):
        # Find the closest topological waypoints to the source and destination (same road and lane)
        source = next(v for (u, v) in self.topology if v.road_id == source.road_id and v.lane_id == source.lane_id)
        destination = next(v for (u, v) in self.topology if v.road_id == destination.road_id and v.lane_id == destination.lane_id)

        # Wrap waypoints in Node objects
        source = Node(source)
        destination = Node(destination)

        # Find the shortest path between the source and destination
        path = nx.shortest_path(self.graph, source=source, target=destination)

        # Return the list of waypoints corresponding to the node ids
        return [node.waypoint for node in path]
