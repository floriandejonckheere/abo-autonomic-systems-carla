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
import threading
import time

from game.game import Game
from game.hud import HUD


TICK = pygame.USEREVENT + 1

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
        default='320x640',
        help='window resolution (default: 320x640)')
    args = argparser.parse_args()
    args.width, args.height = [int(x) for x in args.res.split('x')]

    # Initialize game
    pygame.init()
    pygame.font.init()

    game = None
    t = None

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
        game = Game(world, args.debug, args.milestone_number)

        # Initialize HUD
        hud = HUD(game, args.width, args.height)
        if args.debug:
            world.on_tick(hud.on_world_tick)

        # Setup game (actors, autopilot)
        game.setup()

        # Game (autopilot) loop
        def game_loop():
            clock = pygame.time.Clock()

            while game.running:
                # Limit game loop to 10 FPS
                clock.tick(10)

                game.tick()

        # Start game (autopilot) loop
        t = threading.Thread(target=game_loop)
        t.start()

        # Setup clock
        clock = pygame.time.Clock()

        # Main loop
        while True:
            # Limit main loop to 30 FPS
            clock.tick(30)

            # Update HUD
            if args.debug:
                hud.tick(clock)
                hud.render(display)

                pygame.display.flip()
    except KeyboardInterrupt:
        pass
    finally:
        if game:
            # Stop game (autopilot)
            game.running = False

            game.stop()

            t.join()

        pygame.quit()


if __name__ == '__main__':
    main()
