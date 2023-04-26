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

import pygame

import collections
import datetime

from .features import Features


class HUD:
    def __init__(self, game, width, height):
        self.game = game
        self.width = width
        self.height = height

        self.server_fps = 0
        self.frame_number = 0
        self.simulation_time = 0
        self.map = game.world.get_map().name

        self.features = Features()

        self._info_text = []
        self._server_clock = pygame.time.Clock()

        self._font_mono = pygame.font.Font(pygame.font.match_font('consolas'), 14)

    def on_world_tick(self, timestamp):
        self._server_clock.tick()
        self.server_fps = self._server_clock.get_fps()
        self.frame_number = timestamp.frame_count
        self.simulation_time = timestamp.elapsed_seconds

    def tick(self, clock):
        # Extract features
        self.features.analyze(self.game.autopilot)

        destination = self.game.autopilot.knowledge.get_destination()

        self._info_text = [
            'Server:  % 16.0f FPS' % self.server_fps,
            'Client:  % 16.0f FPS' % clock.get_fps(),
            '',
            'Vehicle: % 20s' % self.features.vehicle,
            'Map:     % 20s' % self.map,
            'Simulation time: % 12s' % datetime.timedelta(seconds=int(self.simulation_time)),
            '',
            'Target speed:% 11.2f km/h' % self.features.target_speed,
            'Speed:   % 15.2f km/h' % self.features.speed,
            u'Heading:% 17.0f\N{DEGREE SIGN} % 2s' % (self.features.rotation.yaw, self.features.heading),
            'Location:% 20s' % ('(% 5.2f, % 5.2f)' % (self.features.location.x, self.features.location.y)),
            'Height:  % 18.0f m' % self.features.location.z,
            '',
            'Destination:% 17s' % ('(% 5.2f, % 5.2f)' % (destination.x, destination.y)),
            'Distance:   % 15.2f m' % self.game.autopilot.knowledge.get_distance_to_destination(),
            '',
            'Reverse:    % 17.2f' % self.features.reverse,
            'Hand brake: % 17s' % self.features.hand_brake,
            '',
            'Throttle:   % 17.2f' % self.features.throttle,
            self.features.throttle_history,
            '',
            'Brake:      % 17.2f' % self.features.brake,
            self.features.brake_history,
            '',
            'Steer:      % 17.2f' % self.features.steer,
            self.features.steer_history,
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
            if isinstance(item, list) or isinstance(item, collections.deque):
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
