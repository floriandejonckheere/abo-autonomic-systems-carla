import statemachine as sm

from .events.broker import broker

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

    def on_enter_idle(self):
        broker.publish('state', 'idle')

    def on_enter_arrived(self):
        broker.publish('state', 'arrived')

    def on_enter_driving(self):
        broker.publish('state', 'driving')

    def on_enter_crashed(self):
        broker.publish('state', 'crashed')

    def on_enter_healing(self):
        broker.publish('state', 'healing')

    def on_enter_parked(self):
        broker.publish('state', 'parked')
