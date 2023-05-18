from ai.carla import carla

import networkx as nx

from .node import Node


class Graph:
    """Weighted directed graph of the topological waypoints on the map."""

    def __init__(self, topology):
        self.topology = topology
        self.graph = nx.DiGraph()

        # Dictionary of parallel edges based on road id (maximum two lanes per road)
        parallel = {(u.road_id, v.road_id): None for (u, v) in topology}

        for (u, v) in topology:
            # Wrap waypoints in Node objects
            u = Node(u)
            v = Node(v)

            # Add edge to graph
            self.graph.add_edge(u, v, weight=u.transform.location.distance(v.transform.location))

            if parallel.get((u.road_id, v.road_id)):
                # A parallel edge already exists, add lane change edges (if allowed)
                u_, v_ = parallel[(u.road_id, v.road_id)]

                if not u.lane_change.name == 'None' and not u.is_intersection:
                    self.graph.add_edge(u, v_, weight=u.transform.location.distance(v_.transform.location))

                if not u_.lane_change.name == 'None' and not u_.is_intersection:
                    self.graph.add_edge(u_, v, weight=u_.transform.location.distance(v.transform.location))
            else:
                # No parallel edge exists, register this edge
                parallel[(u.road_id, v.road_id)] = (u, v)

        print(f'Nodes={len(self.graph.nodes)} Edges={len(self.graph.edges)} Waypoints={len(topology)}')

    # Return the shortest path between two waypoints in the graph
    def shortest_path(self, source, destination):
        # Find the ending waypoint on the edge of the current lane
        source = next(v for (u, v) in self.topology if u.road_id == source.road_id and u.lane_id == source.lane_id)

        # Find the starting waypoint on the edge of the destination lane
        destination = next(u for (u, v) in self.topology if v.road_id == destination.road_id and v.lane_id == destination.lane_id)

        # Wrap waypoints in Node objects
        source = Node(source)
        destination = Node(destination)

        # Find the shortest path between the source and destination
        return nx.dijkstra_path(self.graph, source=source, target=destination)
