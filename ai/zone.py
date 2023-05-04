from typing import Tuple

import numpy as np


class Zone:
    def __init__(self, height: Tuple[int, int], width: Tuple[int, int], color: Tuple[int, int, int]):
        self.height = height
        self.width = width
        self.color = color

    def analyze(self, array):
        # Calculate offsets
        (h0, h1), (w0, w1) = self.dimensions(array)

        # Calculate average of zone
        return np.mean(array[h0:h1, w0:w1])

    def dimensions(self, array):
        height, width, _ = array.shape

        return (
            max(0, min(height - 1, int(self.height[0] * (height / 100)))),
            max(0, min(height - 1, int(self.height[1] * (height / 100)))),
        ), (
            max(0, min(width - 1, int(self.width[0] * (width / 100)))),
            max(0, min(width - 1, int(self.width[1] * (width / 100)))),
        )
