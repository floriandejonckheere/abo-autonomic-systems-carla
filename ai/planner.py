from ai.carla import carla

import time

import ai.goals as goals

from .state.state_machine import StateMachine
from .planning import Navigator, Plan, RecoveryNavigator


class Planner(object):
    """Planner is responsible for creating a plan for moving around, based on the current state of the vehicle."""

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
            # If the vehicle is at a red traffic light, transition to waiting
            if self.knowledge.is_at_traffic_light and self.knowledge.traffic_light.state == carla.TrafficLightState.Red:
                return self.knowledge.state_machine.wait()

            last_healing_at = self.knowledge.state_machine.last_state_at(StateMachine.healing)

            # If there is an obstacle, and the vehicle has not healed recently, transition to healing
            # The healing timeout prevents the vehicle from getting into healing state immediately after recovering
            if (self.knowledge.obstacle or self.knowledge.obstacle_left or self.knowledge.obstacle_right) and (time.time() - last_healing_at > 5.0):
                # Avoid collision with an obstacle (if any)
                self.knowledge.state_machine.heal()
            else:
                # Drive to waypoint
                self.drive()
        elif state == StateMachine.arrived or state == StateMachine.idle:
            # Check for a new destination and plan the path
            if self.knowledge.destination is not None and self.knowledge.location.distance(self.knowledge.destination) > 5.0:
                self.navigator.plan()

            # Drive to new waypoint
            self.drive()
        elif state == StateMachine.waiting:
            # If the traffic light turned green, transition to driving
            if not self.knowledge.is_at_traffic_light or self.knowledge.traffic_light.state == carla.TrafficLightState.Green:
                self.drive()
            else:
                # Wait for traffic lights
                self.knowledge.plan.goals.append(goals.Stop(self.knowledge))
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
        elif state == StateMachine.healing:
            last_event, timestamp = self.knowledge.state_machine.history[-1]

            if time.time() - timestamp < 5.0:
                # If the vehicle is healing, avoid collision with an obstacle
                self.knowledge.plan.goals.append(goals.AvoidCollision(self.knowledge))
            else:
                # Transition to driving state
                self.knowledge.state_machine.drive()
        elif state == StateMachine.recovering:
            last_event, timestamp = self.knowledge.state_machine.history[-1]

            if time.time() - timestamp < 5.0:
                # If the vehicle is recovering, reverse according to the recovery plan
                self.recover()
            else:
                # Clear collision state
                self.knowledge.collision = False

                # Create a new plan
                self.navigator.plan()

                # Transition to driving state
                self.drive()

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
            self.knowledge.update(waypoint=waypoint, distance=self.knowledge.location.distance(waypoint) + self.navigator.distance())

            if not self.knowledge.state_machine.driving.is_active:
                self.knowledge.state_machine.drive()

            # Drive to waypoint
            self.knowledge.plan.goals.append(goals.Drive(self.knowledge))

    def recover(self):
        # Update plan based on current knowledge
        waypoint = self.recovery_navigator.update()

        if waypoint is None:
            # If there are no more waypoints, the vehicle has recovered
            self.knowledge.state_machine.drive()
        else:
            # Otherwise, we keep reversing towards the previous waypoint
            self.knowledge.update(waypoint=waypoint, distance=self.knowledge.location.distance(waypoint) + self.recovery_navigator.distance())

            # Reverse to waypoint
            self.knowledge.plan.goals.append(goals.Reverse(self.knowledge))
