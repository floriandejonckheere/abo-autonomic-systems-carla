import statemachine as sm

from .event_broker import event_broker

class StateMachine(sm.StateMachine):
    idle = sm.State(initial=True)
    arrived = sm.State()
    driving = sm.State()
    crashed = sm.State()
    healing = sm.State()
    parked = sm.State(final=True)

    drive = arrived.to(driving) | driving.to(driving) | idle.to(driving) | healing.to(driving)
    arrive = driving.to(arrived) | arrived.to(arrived)
    crash = driving.to(crashed)
    heal = crashed.to(healing)
    park = driving.to(parked) | arrived.to(parked)

    def on_enter_state(self, event, state):
        event_broker.publish('state_changed', state=state.id, event=event)
