import time

import statemachine as sm


class StateMachine(sm.StateMachine):
    def __init__(self):
        super().__init__()

        self.history = []

    idle = sm.State(initial=True)
    arrived = sm.State()
    driving = sm.State()
    crashed = sm.State()
    healing = sm.State()
    parked = sm.State(final=True)

    drive = arrived.to(driving) | idle.to(driving) | healing.to(driving)
    arrive = driving.to(arrived) | idle.to(arrived)
    crash = arrived.to(crashed) | driving.to(crashed) | idle.to(crashed) | healing.to(crashed)
    heal = driving.to(healing)
    park = driving.to(parked) | arrived.to(parked)

    def on_transition(self, event, state):
        self.history.append((state, time.time()))
