class Goal:
    """Base class for high-level goals."""

    def __init__(self, knowledge):
        self.knowledge = knowledge

    def actions(self):
        return []
