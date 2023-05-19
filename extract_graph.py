#!/usr/bin/env python

import glob
import os
import sys

try:
    sys.path.append(glob.glob('**/*%d.%d-%s.egg' % (
        sys.version_info.major,
        sys.version_info.minor,
        'win-amd64' if os.name == 'nt' else 'linux-x86_64'))[0])
except IndexError:
    pass

import carla

import networkx as nx

from ai.planning.node import Node


client = carla.Client('localhost', 2000)
client.set_timeout(20.0)
world = client.get_world()
map = world.get_map()
topology = map.get_topology()

# Extract topological graph
graph = nx.DiGraph()

for (u, v) in topology:
    # Wrap waypoints in Node objects
    u = Node(u)
    v = Node(v)

    # Add node to graph
    graph.add_node(u.id, x=u.transform.location.x, y=u.transform.location.y)
    graph.add_node(v.id, x=v.transform.location.x, y=v.transform.location.y)

    # Add edge to graph
    graph.add_edge(u.id, v.id, weight=u.transform.location.distance(v.transform.location))

nx.write_graphml(graph, 'graph/01-topology.graphml')
print(f'Wrote {len(graph.nodes)} nodes and {len(graph.edges)} edges to graph/01-topology.graphml')

# Add lane changes to graph
graph = nx.DiGraph()

# Dictionary of parallel edges based on road id (maximum two lanes per road)
parallel = {(u.road_id, v.road_id): None for (u, v) in topology}

for (u, v) in topology:
    # Wrap waypoints in Node objects
    u = Node(u)
    v = Node(v)

    # Add node to graph
    graph.add_node(u.id, x=u.transform.location.x, y=u.transform.location.y)
    graph.add_node(v.id, x=v.transform.location.x, y=v.transform.location.y)

    # Add edge to graph
    graph.add_edge(u.id, v.id, weight=u.transform.location.distance(v.transform.location))

    if parallel.get((u.road_id, v.road_id)):
        # A parallel edge already exists, add lane change edges (if allowed)
        # Lane changes have double the weight of normal edges, to discourage lane changes
        u_, v_ = parallel[(u.road_id, v.road_id)]

        if not u.lane_change.name == 'None' and not u.is_intersection:
            graph.add_edge(u.id, v_.id, weight=2 * u.transform.location.distance(v_.transform.location))

        if not u_.lane_change.name == 'None' and not u_.is_intersection:
            graph.add_edge(u_.id, v.id, weight=2 * u_.transform.location.distance(v.transform.location))
    else:
        # No parallel edge exists, register this edge
        parallel[(u.road_id, v.road_id)] = (u, v)

nx.write_graphml(graph, 'graph/02-lane-changes.graphml')
print(f'Wrote {len(graph.nodes)} nodes and {len(graph.edges)} edges to graph/02-lane-changes.graphml')

# Split up long edges
graph = nx.DiGraph()

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

    # Add node to graph
    graph.add_node(u.id, x=u.transform.location.x, y=u.transform.location.y)
    graph.add_node(v.id, x=v.transform.location.x, y=v.transform.location.y)

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

            graph.add_node(u_next.id, x=u_next.transform.location.x, y=u_next.transform.location.y)

            # Add edge segment to graph (and register segment)
            graph.add_edge(u_previous.id, u_next.id, weight=maximum_length)
            segments.append((u_previous, u_next))

        # Add final edge
        graph.add_edge(u_next.id, v.id, weight=u_next.transform.location.distance(v.transform.location))
        segments.append((u_next, v))

        if parallel.get((u.road_id, v.road_id)):
            # A parallel edge already exists, add lane change edges for all segments (if allowed)
            # Lane changes have double the weight of normal edges, to discourage lane changes
            for (u_, v_), (u__, v__) in zip(segments, parallel_segments[(u.road_id, v.road_id)]):
                if not u_.lane_change.name == 'None' and not u_.is_intersection:
                    graph.add_edge(u_.id, v__.id, weight=2 * u_.transform.location.distance(v__.transform.location))

                if not u__.lane_change.name == 'None' and not u__.is_intersection:
                    graph.add_edge(u__.id, v_.id, weight=2 * u__.transform.location.distance(v_.transform.location))
        else:
            # No parallel edge exists, register this edge
            parallel[(u.road_id, v.road_id)] = (u, v)
            parallel_segments[(u.road_id, v.road_id)] = segments
    else:
        # Add edge to graph
        graph.add_edge(u.id, v.id, weight=u.transform.location.distance(v.transform.location))

        if parallel.get((u.road_id, v.road_id)):
            # A parallel edge already exists, add lane change edges (if allowed)
            # Lane changes have double the weight of normal edges, to discourage lane changes
            u_, v_ = parallel[(u.road_id, v.road_id)]

            if not u.lane_change.name == 'None' and not u.is_intersection:
                graph.add_edge(u.id, v_.id, weight=2 * u.transform.location.distance(v_.transform.location))

            if not u_.lane_change.name == 'None' and not u_.is_intersection:
                graph.add_edge(u_.id, v.id, weight=2 * u_.transform.location.distance(v.transform.location))
        else:
            # No parallel edge exists, register this edge
            parallel[(u.road_id, v.road_id)] = (u, v)

nx.write_graphml(graph, 'graph/03-long-edges.graphml')
print(f'Wrote {len(graph.nodes)} nodes and {len(graph.edges)} edges to graph/03-long-edges.graphml')

exit(0)

# To write the topological path to a file, add the following code to Navigator:
graph = nx.DiGraph()

for i, (u, v) in enumerate(zip(topological_path[:-1], topological_path[1:])):
    graph.add_node(i, x=u.x, y=u.y)
    graph.add_node(i + 1, x=v.x, y=v.y)

    graph.add_edge(i, i + 1, weight=u.distance(v))

nx.write_graphml(graph, 'graph/04-topological-path.graphml')
print(f'Wrote {len(graph.nodes)} nodes and {len(graph.edges)} edges to graph/04-topological-path.graphml')

# To write the detailed path to a file, add the following code to Navigator:
graph = nx.DiGraph()

path = list(self.path)
for i, (u, v) in enumerate(zip(path[:-1], path[1:])):
    graph.add_node(i, x=u.x, y=u.y)
    graph.add_node(i + 1, x=v.x, y=v.y)

    graph.add_edge(i, i + 1, weight=u.distance(v))

nx.write_graphml(graph, 'graph/05-detailed-path.graphml')
print(f'Wrote {len(graph.nodes)} nodes and {len(graph.edges)} edges to graph/05-detailed-path.graphml')

