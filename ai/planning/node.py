from ai.carla import carla


class Node:
    """Node wrapping a waypoint in the topological waypoint graph."""

    def __init__(self, waypoint):
        self.waypoint = waypoint

        # Generate unique id for the node as linear combination of the coordinates
        self.id = (3 * int(100 * waypoint.transform.location.x)) + (5 * int(100 * waypoint.transform.location.y))

    def __eq__(self, other) -> bool:
        return self.id == other.id

    def __ne__(self, other) -> bool:
        return self.id != other.id

    def __hash__(self) -> int:
        return self.id

    def __getattr__(self, name):
        getattr(self.waypoint, name)
