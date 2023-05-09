import statemachine as sm


class StateMachine(sm.StateMachine):
    idle = sm.State(initial=True)
    arrived = sm.State()
    driving = sm.State()
    crashed = sm.State()
    healing = sm.State()
    parked = sm.State(final=True)

    drive = arrived.to(driving) | idle.to(driving) | healing.to(driving)
    arrive = driving.to(arrived) | idle.to(arrived)
    crash = arrived.to(crashed) | driving.to(crashed) | idle.to(crashed)
    heal = driving.to(healing)
    park = driving.to(parked) | arrived.to(parked)
