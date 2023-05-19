from collections import deque


class Value:
    """A class that can be used to store a numerical value and its history."""

    def __init__(self, value=0.0, size=100):
        self.value = value
        self.size = size

        self.history = deque(size * [value], size)

    def update(self, value, ceiling=None):
        self.value = value

        if ceiling is None:
            self.history.append(value)
        else:
            # Relativize points
            self.history.append(min(value / ceiling, ceiling))

    def average(self):
        return sum(self.history) / len(self.history)
