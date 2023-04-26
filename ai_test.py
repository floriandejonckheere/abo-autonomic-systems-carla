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
    argparser.add_argument(
        '--res',
        metavar='WIDTHxHEIGHT',
        default='480x720',
        help='window resolution (default: 480x720)')
    args = argparser.parse_args()
    args.width, args.height = [int(x) for x in args.res.split('x')]

    # Initialize game
    pygame.init()
    pygame.font.init()
    game = None

    try:
        client = carla.Client('localhost', 2000)
        client.set_timeout(20.0)
        world = client.get_world()

        if args.debug:
            # Set pygame window position
            os.environ['SDL_VIDEO_WINDOW_POS'] = "0,30"

            # Initialize pygame window
            display = pygame.display.set_mode(
                (args.width, args.height),
                pygame.HWSURFACE | pygame.DOUBLEBUF)

        # Initialize game context
        game = Game(world, args.debug, args.milestone_number, args.width, args.height, display)

        # Setup game (actors, autopilot)
        game.setup()

        # Setup clock
        clock = pygame.time.Clock()

        # Main loop
        while game.running:
            clock.tick_busy_loop(60)

            game.tick(clock)

            if args.debug:
                game.hud.render(display)
                pygame.display.flip()

    finally:
        game and game.stop()

        pygame.quit()

if __name__ == '__main__':
    main()
