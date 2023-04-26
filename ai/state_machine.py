import statemachine as sm


class StateMachine(sm.StateMachine):
    arrived = sm.State()
    driving = sm.State()
    crashed = sm.State()
    healing = sm.State()
    undefined = sm.State(initial=True)

    drive = arrived.to(driving) | driving.to(driving) | undefined.to(driving) | healing.to(driving)
    arrive = driving.to(arrived) | arrived.to(arrived)
    crash = driving.to(crashed)
    heal = crashed.to(healing)

    def __init__(self):
        super().__init__()

        self.arrived_callback = lambda *_, **__: None
        self.crashed_callback = lambda *_, **__: None

    def on_enter_arrived(self):
        self.arrived_callback()

    def on_enter_crashed(self):
        self.crashed_callback()