from collections import deque

class Value:
    """A value that can be used to store a float value and its history."""

    def __init__(self, value=0.0, size=100):
        self.value = value
        self.history = deque(size * [0.0], size)

    def update(self, value, ceiling=None):
        self.value = value

        if ceiling is None:
            self.history.append(value)
        else:
            # Relativize points
            self.history.append(min(value / ceiling, ceiling))
