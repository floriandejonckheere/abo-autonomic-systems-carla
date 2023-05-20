import time

from collections import deque

import statemachine as sm


class StateMachine(sm.StateMachine):
    """System state machine for the vehicle."""

    def __init__(self):
        super().__init__()

        # History of state transitions
        self.history = deque(maxlen=10)

    idle = sm.State(initial=True)
    arrived = sm.State()
    driving = sm.State()
    crashed = sm.State()
    healing = sm.State()
    recovering = sm.State()
    waiting = sm.State()
    parked = sm.State(final=True)

    drive = arrived.to(driving) | idle.to(driving) | healing.to(driving) | recovering.to(driving) | waiting.to(driving)
    arrive = driving.to(arrived) | idle.to(arrived)
    crash = arrived.to(crashed) | driving.to(crashed) | idle.to(crashed) | healing.to(crashed)
    heal = driving.to(healing)
    park = driving.to(parked) | arrived.to(parked)
    recover = crashed.to(recovering)
    wait = driving.to(waiting)

    def on_transition(self, event, state):
        self.history.append((state, time.time()))
