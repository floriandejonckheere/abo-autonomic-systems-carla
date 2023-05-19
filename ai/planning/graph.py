from ai.carla import carla

import networkx as nx

from .node import Node


class Graph:
    """Weighted directed graph of the topological waypoints on the map."""

    def __init__(self, topology):
        self.topology = topology
        self.graph = nx.DiGraph()

        # Maximum edge length before splitting into multiple edges
        maximum_length = 50

        # Dictionary of parallel edges based on road id (maximum two lanes per road)
        parallel = {(u.road_id, v.road_id): None for (u, v) in topology}

        # Dictionary of parallel edge segments based on road id
        parallel_segments = {(u.road_id, v.road_id): [] for (u, v) in topology}

        for (u, v) in topology:
            # Wrap waypoints in Node objects
            u = Node(u)
            v = Node(v)

            distance = u.transform.location.distance(v.transform.location)

            if distance > maximum_length:
                # Split up long edges into multiple edges
                u_previous = None
                u_next = u

                segments = []

                for i in range(int(distance // maximum_length)):
                    u_previous = u_next

                    # Generate a new waypoint every N meters
                    u_next = Node(u_next.next(maximum_length)[0])

                    # Add edge segment to graph (and register segment)
                    self.graph.add_edge(u_previous, u_next, weight=maximum_length)
                    segments.append((u_previous, u_next))

                # Add final edge
                self.graph.add_edge(u_next, v, weight=u_next.transform.location.distance(v.transform.location))
                segments.append((u_next, v))

                if parallel.get((u.road_id, v.road_id)):
                    # A parallel edge already exists, add lane change edges for all segments (if allowed)
                    # Lane changes have double the weight of normal edges, to discourage lane changes
                    for (u_, v_), (u__, v__) in zip(segments, parallel_segments[(u.road_id, v.road_id)]):
                        if not u_.lane_change.name == 'None' and not u_.is_intersection:
                            self.graph.add_edge(u_, v__, weight=2*u_.transform.location.distance(v__.transform.location))

                        if not u__.lane_change.name == 'None' and not u__.is_intersection:
                            self.graph.add_edge(u__, v_, weight=2*u__.transform.location.distance(v_.transform.location))
                else:
                    # No parallel edge exists, register this edge
                    parallel[(u.road_id, v.road_id)] = (u, v)
                    parallel_segments[(u.road_id, v.road_id)] = segments
            else:
                # Add edge to graph
                self.graph.add_edge(u, v, weight=u.transform.location.distance(v.transform.location))

                if parallel.get((u.road_id, v.road_id)):
                    # A parallel edge already exists, add lane change edges (if allowed)
                    # Lane changes have double the weight of normal edges, to discourage lane changes
                    u_, v_ = parallel[(u.road_id, v.road_id)]

                    if not u.lane_change.name == 'None' and not u.is_intersection:
                        self.graph.add_edge(u, v_, weight=2*u.transform.location.distance(v_.transform.location))

                    if not u_.lane_change.name == 'None' and not u_.is_intersection:
                        self.graph.add_edge(u_, v, weight=2*u_.transform.location.distance(v.transform.location))
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
