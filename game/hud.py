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

import collections
import datetime

import numpy as np

from ai.analyzer import DEPTH_ZONES

from .features import Features

COLORS = [
    (255, 136, 0),
    (136, 255, 0),
    (0, 255, 136),
    (0, 136, 255),
    (136, 0, 255),
    (255, 0, 136),
]


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

        self._last_depth_image_frame_number = 0
        self._last_depth_image = None

    def on_world_tick(self, timestamp):
        self._server_clock.tick()
        self.server_fps = self._server_clock.get_fps()
        self.frame_number = timestamp.frame_count
        self.simulation_time = timestamp.elapsed_seconds

    def tick(self, clock):
        # Extract features
        self.features.analyze(self.game.autopilot)

        destination = self.game.autopilot.knowledge.destination
        waypoint = self.game.autopilot.knowledge.waypoint

        goals_and_actions = []
        for goal in self.features.goals:
            name = type(goal).__name__
            actions = ', '.join([type(action).__name__ for action in goal.actions()])
            actions = 'None' if not actions else actions

            goals_and_actions.append(f'  {name}: {actions}')

        self._info_text = [
            'Server:  % 25.0f FPS' % self.server_fps,
            'Client:  % 25.0f FPS' % clock.get_fps(),
            '',
            'Vehicle: % 29s' % self.features.vehicle,
            'Map:     % 29s' % self.map,
            'Simulation time: % 12s' % datetime.timedelta(seconds=int(self.simulation_time)),
            '',
            u'Heading:% 26.0f\N{DEGREE SIGN} % 2s' % (self.features.rotation.yaw, self.features.heading),
            'Location:% 29s' % ('(% 5.2f, % 5.2f)' % (self.features.location.x, self.features.location.y)),
            'Height:  % 27.0f m' % self.features.location.z,
            '',
            'Destination:% 26s' % ('(% 5.2f, % 5.2f)' % (destination.x, destination.y)),
            'Waypoint:   % 26s' % ('(% 5.2f, % 5.2f)' % (waypoint.x, waypoint.y)),
            'Distance:   % 24.2f m' % self.game.autopilot.knowledge.location.distance(self.game.autopilot.knowledge.waypoint),
            '',
            'Reverse:    % 26.2f' % self.features.reverse,
            'Hand brake: % 26s' % self.features.hand_brake,
            '',
            'Throttle:   % 26.2f' % self.features.throttle,
            self.features.throttle_history,
            '',
            'Brake:      % 26.2f' % self.features.brake,
            self.features.brake_history,
            '',
            'Target speed:% 20.2f km/h' % self.features.target_speed,
            'Speed:       % 20.2f km/h' % self.features.speed,
            [self.features.target_speed_history, self.features.speed_history],
            '',
            'Steer:      % 26.2f' % self.features.steer,
            self.features.steer_history,
            '',
            'Proximity: % 26.2f' % self.features.proximity,
            [self.features.proximity_history, self.features.proximity_left_history, self.features.proximity_right_history],
            '',
            'State:  % 30s' % self.features.state,
            *goals_and_actions,
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
                    if isinstance(item[0], list) or isinstance(item[0], collections.deque):
                        # Two-dimensional list
                        for i, series in enumerate(item):
                            points = [(x + 8, v_offset + 8 + (1.0 - y) * 30) for x, y in enumerate(series)]
                            pygame.draw.lines(display, COLORS[i], False, points, 1)
                    else:
                        # One-dimensional list
                        points = [(x + 8, v_offset + 8 + (1.0 - y) * 30) for x, y in enumerate(item)]
                        pygame.draw.lines(display, (136, 255, 0), False, points, 2)
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

        # Render depth image
        if self.features.depth_image is not None:
            # Render image only if it has changed
            if self.features.depth_image.frame_number > self._last_depth_image_frame_number:
                self._last_depth_image_frame_number = self.features.depth_image.frame_number

                array = np.frombuffer(self.features.depth_image.raw_data, dtype=np.dtype("uint8"))
                array = np.reshape(array, (self.features.depth_image.height, self.features.depth_image.width, 4))
                array = array[:, :, :3]
                array = array[:, :, ::-1]

                # Mark sensor zones on image
                array = np.copy(array)

                for zone in DEPTH_ZONES.values():
                    (h0, h1), (w0, w1) = zone.dimensions(array)

                    # Draw vertical lines
                    for h in range(h0, h1):
                        for w in (w0, w1):
                            array[h, w] = zone.color

                    # Draw horizontal lines
                    for h in (h0, h1):
                        for w in range(w0, w1):
                            array[h, w] = zone.color

                self._last_depth_image = pygame.surfarray.make_surface(array.swapaxes(0, 1))

            display.blit(self._last_depth_image, (320, 0))
