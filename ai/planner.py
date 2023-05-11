import time

import ai.goals as goals

from .state_machine import StateMachine
from .planning import Navigator, Plan, RecoveryNavigator


# Planner is responsible for creating a plan for moving around
# In our case it creates a list of waypoints to follow so that vehicle arrives at destination
# Alternatively this can also provide a list of waypoints to try avoid crashing or 'uncrash' itself
class Planner(object):
    def __init__(self, knowledge, vehicle, debug):
        self.knowledge = knowledge
        self.vehicle = vehicle
        self.debug = debug

        self.navigator = Navigator(knowledge, vehicle.get_world(), debug)
        self.recovery_navigator = RecoveryNavigator(knowledge, vehicle.get_world(), debug)

    # Function that is called at time intervals to update ai-state
    def update(self, dt):
        # Set new, empty plan
        self.knowledge.plan = Plan()

        state = self.knowledge.state_machine.current_state

        if state == StateMachine.driving:
            # Drive to waypoint
            self.drive()
        elif state == StateMachine.healing:
            # Avoid collision with an obstacle
            self.knowledge.plan.goals.append(goals.AvoidCollision(self.knowledge))
        elif state == StateMachine.arrived or state == StateMachine.idle:
            # Check for a new destination and plan the path
            if self.knowledge.destination is not None and self.knowledge.location.distance(self.knowledge.destination) > 5.0:
                self.navigator.plan()

            # Drive to new waypoint
            # FIXME: vehicle will end up in an infinite loop if the destination is not changed from outside
            self.drive()
        elif state == StateMachine.parked:
            # If the vehicle is parking, apply handbrake and do nothing
            self.knowledge.plan.goals.append(goals.Park(self.knowledge))
        elif state == StateMachine.crashed:
            last_event, timestamp = self.knowledge.state_machine.history[-1]

            if time.time() - timestamp < 3.0:
                # If the vehicle has crashed, stop and do nothing
                self.knowledge.plan.goals.append(goals.Stop(self.knowledge))
            else:
                # Create a recovery plan (reverse according to the location history)
                self.recovery_navigator.plan()

                # Transition to recovering state
                self.knowledge.state_machine.recover()
        elif state == StateMachine.recovering:
            # Recover from crash
            self.recover()
        else:
            raise RuntimeError(f'Invalid state: {state}')

    def drive(self):
        # Update plan based on current knowledge
        waypoint = self.navigator.update()

        if waypoint is None:
            # If there are no more waypoints, the vehicle has arrived
            if not self.knowledge.state_machine.arrived.is_active:
                self.knowledge.state_machine.arrive()

            self.knowledge.plan.goals.append(goals.Park(self.knowledge))
        else:
            # Otherwise, we keep driving towards the next waypoint
            self.knowledge.update(waypoint=waypoint)

            if not self.knowledge.state_machine.driving.is_active:
                self.knowledge.state_machine.drive()

            # Drive to waypoint
            self.knowledge.plan.goals.append(goals.Drive(self.knowledge))

            # Wait for traffic lights
            self.knowledge.plan.goals.append(goals.Wait(self.knowledge))

    def recover(self):
        # Update plan based on current knowledge
        waypoint = self.recovery_navigator.update()

        if waypoint is None:
            # If there are no more waypoints, the vehicle has recovered
            self.knowledge.state_machine.drive()
        else:
            # Otherwise, we keep reversing towards the previous waypoint
            self.knowledge.update(waypoint=waypoint)

            # Reverse to waypoint
            self.knowledge.plan.goals.append(goals.Reverse(self.knowledge))
