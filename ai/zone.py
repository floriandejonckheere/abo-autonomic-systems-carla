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
        print(self.height, self.width, array.shape)

        return (
            int(self.height[0] * (array.shape[0] / 100)),
            int(self.height[1] * (array.shape[0] / 100))
        ), (
            int(self.width[0] * (array.shape[1] / 100)),
            int(self.width[1] * (array.shape[1] / 100))
        )
