import glob
import os
import sys

try:
    sys.path.append(glob.glob('../**/*%d.%d-%s.egg' % (
        sys.version_info.major,
        sys.version_info.minor,
        'win-amd64' if os.name == 'nt' else 'linux-x86_64'))[0])
except IndexError:
    pass

import carla
import pygame

import datetime
import math
import random

from ai.autopilot import Autopilot


def get_actor_display_name(actor, truncate=250):
    name = ' '.join(actor.type_id.replace('_', '.').title().split('.')[1:])
    return (name[:truncate - 1] + u'\u2026') if len(name) > truncate else name

class HUD:
    def __init__(self, game, width, height):
        self.game = game
        self.width = width
        self.height = height

        self.server_fps = 0
        self.frame_number = 0
        self.simulation_time = 0

        self._info_text = []
        self._server_clock = pygame.time.Clock()

        self._font_mono = pygame.font.Font(pygame.font.match_font('consolas'), 14)

    def on_world_tick(self, timestamp):
        self._server_clock.tick()
        self.server_fps = self._server_clock.get_fps()
        self.frame_number = timestamp.frame_count
        self.simulation_time = timestamp.elapsed_seconds

    def tick(self, game, clock):
        t = game.autopilot.vehicle.get_transform()
        v = game.autopilot.vehicle.get_velocity()
        c = game.autopilot.vehicle.get_control()

        heading = 'N' if abs(t.rotation.yaw) < 89.5 else ''
        heading += 'S' if abs(t.rotation.yaw) > 90.5 else ''
        heading += 'E' if 179.5 > t.rotation.yaw > 0.5 else ''
        heading += 'W' if -0.5 > t.rotation.yaw > -179.5 else ''

        vehicles = game.world.get_actors().filter('vehicle.*')

        destination = game.autopilot.knowledge.get_destination()

        self._info_text = [
            'Server:  % 16.0f FPS' % self.server_fps,
            'Client:  % 16.0f FPS' % clock.get_fps(),
            '',
            'Vehicle: % 20s' % get_actor_display_name(game.autopilot.vehicle, truncate=20),
            'Map:     % 20s' % game.world.get_map().name,
            'Simulation time: % 12s' % datetime.timedelta(seconds=int(self.simulation_time)),
            '',
            'Target speed:% 11.2f km/h' % game.autopilot.knowledge.get_target_speed(),
            'Speed:   % 15.2f km/h' % (3.6 * math.sqrt(v.x**2 + v.y**2 + v.z**2)),
            u'Heading:% 17.0f\N{DEGREE SIGN} % 2s' % (t.rotation.yaw, heading),
            'Location:% 20s' % ('(% 5.2f, % 5.2f)' % (t.location.x, t.location.y)),
            'Height:  % 18.0f m' % t.location.z,
            '',
            'Destination:% 17s' % ('(% 5.2f, % 5.2f)' % (destination.x, destination.y)),
            'Distance:   % 15.2f m' % game.autopilot.knowledge.get_distance_to_destination(),
            '',
            'Throttle:   % 17.2f' % c.throttle,
            'Steer:      % 17.2f' % c.steer,
            'Brake:      % 17.2f' % c.brake,
            'Reverse:    % 17.2f' % c.reverse,
            'Hand brake: % 17s' % c.hand_brake,
            'Number of vehicles: % 9d' % len(vehicles),
        ]

    def render(self, display):
        info_surface = pygame.Surface((self.width, self.height))
        info_surface.set_alpha(100)
        display.blit(info_surface, (0, 0))

        v_offset = 4
        bar_h_offset = 100
        bar_width = 106
        for item in self._info_text:
            if v_offset + 18 > self.height:
                break
            if isinstance(item, list):
                if len(item) > 1:
                    points = [(x + 8, v_offset + 8 + (1.0 - y) * 30) for x, y in enumerate(item)]
                    pygame.draw.lines(display, (255, 136, 0), False, points, 2)
                item = None
                v_offset += 18
            elif isinstance(item, tuple):
                if isinstance(item[1], bool):
                    rect = pygame.Rect((bar_h_offset, v_offset + 8), (6, 6))
                    pygame.draw.rect(display, (255, 255, 255), rect, 0 if item[1] else 1)
                else:
                    rect_border = pygame.Rect((bar_h_offset, v_offset + 8), (bar_width, 6))
                    pygame.draw.rect(display, (255, 255, 255), rect_border, 1)
                    f = (item[1] - item[2]) / (item[3] - item[2])
                    if item[2] < 0.0:
                        rect = pygame.Rect((bar_h_offset + f * (bar_width - 6), v_offset + 8), (6, 6))
                    else:
                        rect = pygame.Rect((bar_h_offset, v_offset + 8), (f * bar_width, 6))
                    pygame.draw.rect(display, (255, 255, 255), rect)
                item = item[0]
            if item:  # At this point has to be a str.
                surface = self._font_mono.render(item, True, (255, 255, 255))
                display.blit(surface, (8, v_offset))
            v_offset += 18
