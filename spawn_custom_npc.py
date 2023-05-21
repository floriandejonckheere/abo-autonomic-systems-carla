#!/usr/bin/env python

# Copyright (c) 2017 Computer Vision Center (CVC) at the Universitat Autonoma de
# Barcelona (UAB).
#
# This work is licensed under the terms of the MIT license.
# For a copy, see <https://opensource.org/licenses/MIT>.

"""Spawn NPCs into the simulation"""

import glob
import os
import sys

os.environ['FOR_DISABLE_CONSOLE_CTRL_HANDLER'] = '1'

try:
    sys.path.append(glob.glob('**/*%d.%d-%s.egg' % (
        sys.version_info.major,
        sys.version_info.minor,
        'win-amd64' if os.name == 'nt' else 'linux-x86_64'))[0])
except IndexError:
    pass

import carla

import argparse
import random
import threading

from game.scenarios.random import Random
from game.simulation import Simulation

def main():
    argparser = argparse.ArgumentParser(
        description=__doc__)
    argparser.add_argument(
        '--host',
        metavar='H',
        default='127.0.0.1',
        help='IP of the host server (default: 127.0.0.1)')
    argparser.add_argument(
        '-p', '--port',
        metavar='P',
        default=2000,
        type=int,
        help='TCP port to listen to (default: 2000)')
    argparser.add_argument(
        '-n', '--number-of-vehicles',
        metavar='N',
        default=10,
        type=int,
        help='number of vehicles (default: 10)')
    argparser.add_argument(
        '-d', '--delay',
        metavar='D',
        default=2.0,
        type=float,
        help='delay in seconds between spawns (default: 2.0)')
    argparser.add_argument(
        '--seed',
        metavar='S',
        default=None,
        type=int,
        help='Seed for the random number generator')
    args = argparser.parse_args()

    # Initialize RNG
    seed = args.seed if args.seed is not None else random.randrange(sys.maxsize)
    print(f'Using random seed {seed}')
    random.seed(seed)

    # Write seed to file
    with open('seed.txt', 'a') as f:
        f.write(f'{seed}\n')

    simulations = []

    try:
        client = carla.Client(args.host, args.port)
        client.set_timeout(20.0)
        world = client.get_world()

        for i in range(0, args.number_of_vehicles):
            # Initialize simulation context with random destinations
            simulation = Simulation(world, args.debug, args.profile, 'Random')

            # Add simulation to list of simulations
            simulations.append(simulation)

            # Start simulation (in a separate thread)
            simulation.start()

        # Wait for all simulations to finish
        for simulation in simulations:
            simulation.thread.join()
    except KeyboardInterrupt:
        pass
    finally:
        for simulation in simulations:
            simulation.stop()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        pass
    finally:
        print('\ndone.')
