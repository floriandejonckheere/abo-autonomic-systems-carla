class Goal:
    """Base class for high-level goals."""

    def __init__(self, knowledge, emergency=False):
        self.knowledge = knowledge
        self.emergency = emergency

    def actions(self):
        return []
