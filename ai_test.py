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

from game.game import Game
from game.hud import HUD


TICK = pygame.USEREVENT + 1

def main():
    argparser = argparse.ArgumentParser(
        description=__doc__)
    argparser.add_argument(
        '-m', '--milestone-number',
        metavar='M',
        default=None,
        type=int,
        help='Milestone number (default: 1)')
    argparser.add_argument(
        '-s', '--scenario',
        metavar='S',
        default='MilestoneOne',
        type=str,
        help='Scenario (default: MilestoneOne)'
    )
    argparser.add_argument(
        '-d', '--debug',
        metavar='D',
        default=False,
        type=bool,
        help='Enable debug view (default: false)')
    argparser.add_argument(
        '--res',
        metavar='WIDTHxHEIGHT',
        default='640x720',
        help='window resolution (default: 640x720)')
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

        # Map milestone number to scenario for backwards compatibility
        if args.milestone_number:
            args.scenario = {1: "MilestoneOne", 2: "MilestoneTwo", 3: "MilestoneThree", 4: "MilestoneFour"}[args.milestone_number]

        # Initialize game context
        game = Game(world, args.debug, args.scenario)

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
                game.tick()

                # Limit game loop to 10 FPS
                clock.tick(10)

        # Start game (autopilot) loop
        t = threading.Thread(target=game_loop)
        t.start()

        # Setup clock
        clock = pygame.time.Clock()

        # Main loop
        while True:
            # Limit main loop to 30 FPS
            clock.tick(30)

            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    break

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

        pygame.display.quit()
        pygame.quit()


if __name__ == '__main__':
    main()
