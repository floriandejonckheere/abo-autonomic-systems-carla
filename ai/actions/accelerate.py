import numpy as np
import skfuzzy as fz

from skfuzzy import control as ctrl

from .action import Action


class Accelerate(Action):
    """Apply throttle and release brake based on distance and delta speed."""

    def __init__(self, distance, speed, target_speed):
        self.distance = distance
        self.speed = speed
        self.target_speed = target_speed

        # Input variables
        x_distance = np.arange(0, 1000, 1)
        x_delta_speed = np.linspace(-50, 50, 200)

        # Output variables
        x_throttle = np.arange(0, 1, 0.01)
        x_brake = np.arange(-1, 1, 0.01)

        # Antecedents
        distance = ctrl.Antecedent(x_distance, 'distance')
        delta_speed = ctrl.Antecedent(x_delta_speed, 'delta_speed')

        # Consequents
        throttle = ctrl.Consequent(x_throttle, 'throttle')
        brake = ctrl.Consequent(x_brake, 'brake')

        # Membership functions
        distance['low'] = fz.zmf(x_distance, 0, 60)
        distance['medium'] = fz.gaussmf(x_distance, 15, 5)
        distance['high'] = fz.smf(x_distance, 10, 50)

        # Aim for slightly negative delta speed (little faster than target speed)
        delta_speed['low'] = fz.zmf(x_delta_speed, -3, 30)
        delta_speed['medium'] = fz.smf(x_delta_speed, -3, 30)

        throttle['off'] = fz.zmf(x_throttle, 0, 0.01)
        throttle['medium'] = fz.gaussmf(x_throttle, 0.3, 0.2)
        throttle['high'] = fz.smf(x_throttle, 0.5, 0.8)

        brake['off'] = fz.zmf(x_brake, -0.3, 0)
        brake['low'] = fz.zmf(x_brake, 0, 0.3)

        # Rules
        # If the vehicle is far away (and not close to the speed limit), accelerate
        rule1 = ctrl.Rule(antecedent=(distance['high'] & delta_speed['medium']),
                          consequent=(throttle['high'], brake['off']), label='rule1')

        # If the vehicle is getting closer to the target (and not close to the speed limit), let off the throttle
        rule2 = ctrl.Rule(antecedent=(distance['medium'] & delta_speed['medium']),
                          consequent=(throttle['medium'], brake['off']), label='rule2')

        # If the vehicle is close to the target or the speed limit is being exceeded, brake softly
        rule3 = ctrl.Rule(antecedent=(distance['low'] | delta_speed['low']),
                          consequent=(throttle['off'], brake['low']), label='rule3')

        # Control system
        fuzzy_control = ctrl.ControlSystem(rules=[rule1, rule2, rule3])

        # Control system simulation
        self.fuzzy_simulation = ctrl.ControlSystemSimulation(fuzzy_control)

    def apply(self, control):
        # Set fuzzy control system inputs
        self.fuzzy_simulation.inputs({'distance': self.distance, 'delta_speed': self.target_speed - self.speed})

        # Crunch the numbers
        self.fuzzy_simulation.compute()

        # Set throttle and brake
        control.throttle = np.clip(self.fuzzy_simulation.output['throttle'], 0, 1)
        control.brake = np.clip(self.fuzzy_simulation.output['brake'], 0, 1)

        print(f'd={self.distance:.2f} ds={self.target_speed - self.speed:.2f} t={control.throttle:.2f} b={control.brake:.2f}')
