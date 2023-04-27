import statemachine as sm

from .event_broker import event_broker


class StateMachine(sm.StateMachine):
    idle = sm.State(initial=True)
    arrived = sm.State()
    driving = sm.State()
    crashed = sm.State()
    healing = sm.State()
    parked = sm.State(final=True)

    drive = driving.to(driving) | arrived.to(driving) | idle.to(driving) | healing.to(driving)
    arrive = arrived.to(arrived) | driving.to(arrived)
    crash = crashed.to(crashed) | arrived.to(crashed) | driving.to(crashed) | idle.to(crashed)
    heal = healing.to(healing) | crashed.to(healing)
    park = driving.to(parked) | arrived.to(parked)

    def on_enter_state(self, event, state):
        event_broker.publish('state_changed', state=state.id, event=event)
