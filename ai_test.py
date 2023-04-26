#!/usr/bin/env python

# Copyright (c) 2017 Computer Vision Center (CVC) at the Universitat Autonoma de
# Barcelona (UAB).
#
# This work is licensed under the terms of the MIT license.
# For a copy, see <https://opensource.org/licenses/MIT>.

import glob
import os
import sys

try:
    sys.path.append(glob.glob('**/*%d.%d-%s.egg' % (
        sys.version_info.major,
        sys.version_info.minor,
        'win-amd64' if os.name == 'nt' else 'linux-x86_64'))[0])
except IndexError:
    pass

import carla
import pygame

import time
import argparse

from game.game import Game


def main():
    argparser = argparse.ArgumentParser(
        description=__doc__)
    argparser.add_argument(
        '-m', '--milestone-number',
        metavar='M',
        default=1,
        type=int,
        help='Milestone number (default: 1)')
    argparser.add_argument(
        '-d', '--debug',
        metavar='D',
        default=False,
        type=bool,
        help='Enable debug view (default: false)')
    args = argparser.parse_args()

    # Initialize game context
    game = None

    try:
        client = carla.Client('localhost', 2000)
        client.set_timeout(20.0)
        world = client.get_world()

        # Initialize game context
        game = Game(world, args.debug, args.milestone_number)

        # Setup game (actors, autopilot)
        game.setup()

        # Main loop
        ctr = 0
        while game.running:
            status = game.tick()
            if status == None:
                ctr += 1
                if ctr > 3:
                    game.running = False
            else:
                ctr = 0

            time.sleep(0.1)
    finally:
        game and game.stop()

        pygame.quit()

if __name__ == '__main__':
    main()
