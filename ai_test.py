#!/usr/bin/env python

# Copyright (c) 2017 Computer Vision Center (CVC) at the Universitat Autonoma de
# Barcelona (UAB).
#
# This work is licensed under the terms of the MIT license.
# For a copy, see <https://opensource.org/licenses/MIT>.

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
import pygame

from pygame.locals import K_ESCAPE, K_l, K_q

import argparse
import random

from game.simulation import Simulation
from game.hud import HUD


TICK = pygame.USEREVENT + 1

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
        help='Scenario (default: MilestoneOne)')
    argparser.add_argument(
        '-d', '--debug',
        default=False,
        action='store_true',
        help='Enable debug view (default: false)')
    argparser.add_argument(
        '-f', '--follow',
        default=False,
        action='store_true',
        help='Position camera behind the newly spawned vehicle (default: false)')
    argparser.add_argument(
        '--res',
        metavar='WIDTHxHEIGHT',
        default='640x840',
        help='window resolution (default: 640x840)')
    argparser.add_argument(
        '--seed',
        metavar='S',
        default=None,
        type=int,
        help='Seed for the random number generator')
    argparser.add_argument(
        '--profile',
        default=False,
        action='store_true',
        help='Enable profiling (default: false)')
    args = argparser.parse_args()
    args.width, args.height = [int(x) for x in args.res.split('x')]

    # Initialize RNG
    seed = args.seed if args.seed is not None else random.randrange(sys.maxsize)
    print(f'Using random seed {seed}')
    random.seed(seed)

    # Write seed to file
    with open('seed.txt', 'a') as f:
        f.write(f'{seed}\n')

    # Initialize game
    pygame.init()
    pygame.font.init()

    simulation = None

    try:
        client = carla.Client(args.host, args.port)
        client.set_timeout(20.0)
        world = client.get_world()

        # Actors that were not properly cleaned up
        actors = [a for a in world.get_actors() if a.type_id.startswith('vehicle') or a.type_id.startswith('sensor')]

        if actors:
            print(f'WARNING: {len(actors)} additional actors in the world, cleaning up...')

        for actor in actors:
            actor.destroy()

        # Initialize HUD
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

        # Initialize simulation context
        simulation = Simulation(world, args.debug, args.profile, args.scenario)

        # Start simulation (in a separate thread)
        simulation.start()

        # Setup clock
        clock = pygame.time.Clock()

        # Initialize HUD
        hud = HUD(simulation, args.width, args.height)
        if args.debug:
            world.on_tick(hud.on_world_tick)

        if args.follow:
            # Move camera behind the new vehicle
            transform = simulation.autopilot.vehicle.get_transform()

            vector = transform.get_forward_vector()
            vector += carla.Vector3D(x=6*vector.x, y=6*vector.y, z=-5)

            world.get_spectator().set_transform(
                carla.Transform(
                    transform.location - vector,
                    carla.Rotation(pitch=-20, yaw=transform.rotation.yaw),
                )
            )
        # Main loop
        while True:
            # Limit main loop to 30 FPS
            clock.tick(30)

            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    break
                elif event.type == pygame.KEYUP:
                    if event.key == K_q or event.key == K_ESCAPE:
                        return
                    elif event.key == K_l:
                        # Save LIDAR image
                        image = simulation.autopilot.knowledge.lidar_image
                        frame = image.frame_number
                        file = '_out/%s/%08d' % (args.scenario, frame)
                        image.save_to_disk(file)
                        print(f'LIDAR image saved to {file}.ply')

                        # Save RGB image
                        image = simulation.autopilot.knowledge.rgb_image
                        file = '_out/%s/%08d' % (args.scenario, frame)
                        image.save_to_disk(file)
                        print(f'RGB image saved to {file}.png')

            # Update HUD
            if args.debug:
                hud.tick(clock)
                hud.render(display)

                pygame.display.flip()
    except KeyboardInterrupt:
        pass
    finally:
        simulation.stop()

        pygame.display.quit()
        pygame.quit()


if __name__ == '__main__':
    main()
