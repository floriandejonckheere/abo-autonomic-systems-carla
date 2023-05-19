from .action import Action


class Shift(Action):
    """Shift gears to reverse or drive."""

    def __init__(self, reverse):
        self.reverse = reverse

    def apply(self, control):
        control.reverse = self.reverse
