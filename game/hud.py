from ai.carla import carla

import pygame

import collections
import datetime

import numpy as np

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

        self.features = Features(size=(320 - 2 * 8))

        self._info_text = []
        self._server_clock = pygame.time.Clock()

        self._font_mono = pygame.font.Font(pygame.font.match_font('consolas'), 14)

        self._last_proximity_image_frame_number = 0
        self._last_proximity_image = None

        self._last_rgb_image_frame_number = 0
        self._last_rgb_image = None

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
            'Simulation time: % 21s' % datetime.timedelta(seconds=int(self.simulation_time)),
            '',
            u'Heading:% 26.0f\N{DEGREE SIGN} % 2s' % (self.features.rotation.yaw, self.features.heading),
            'Location:% 29s' % ('(% 5.2f, % 5.2f)' % (self.features.location.x, self.features.location.y)),
            'Height:  % 27.0f m' % self.features.location.z,
            '',
            'Destination:% 26s' % ('(% 5.2f, % 5.2f)' % (destination.x, destination.y)),
            'Waypoint:   % 26s' % ('(% 5.2f, % 5.2f)' % (waypoint.x, waypoint.y)),
            'Distance:   % 24.2f m' % self.game.autopilot.knowledge.location.distance(self.game.autopilot.knowledge.waypoint),
            '',
            'Collision: % 27s' % self.features.collision,
            'Lane detector: % 23s' % ', '.join([l.name for l in self.features.lane_invasion]),
            '',
            'Reverse:    % 26.2f' % self.features.reverse,
            'Hand brake: % 26s' % self.features.hand_brake,
            '',
            'Throttle:   % 26.2f' % self.features.throttle.value,
            self.features.throttle.history,
            '',
            'Brake:      % 26.2f' % self.features.brake.value,
            self.features.brake.history,
            '',
            'Steer:      % 26.2f' % self.features.steer.value,
            self.features.steer.history,
            '',
            'Target speed:% 20.2f km/h' % self.features.target_speed.value,
            'Speed:       % 20.2f km/h' % self.features.speed.value,
            [self.features.target_speed.history, self.features.speed.history],
            '',
            'Proximity: % 10.2f' % self.features.proximity.value,
            self.features.proximity.history,
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
                            array = [(x + 8, v_offset + 8 + (1.0 - y) * 30) for x, y in enumerate(series)]
                            pygame.draw.lines(display, COLORS[i], False, array, 1)
                    else:
                        # One-dimensional list
                        array = [(x + 8, v_offset + 8 + (1.0 - y) * 30) for x, y in enumerate(item)]
                        pygame.draw.lines(display, (136, 255, 0), False, array, 2)
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

        # Render proximity images
        if self.features.proximity_image is not None:
            # Render image only if it has changed
            if self.features.proximity_image.frame_number > self._last_proximity_image_frame_number:
                self._last_proximity_image_frame_number = self.features.proximity_image.frame_number

                array = np.frombuffer(self.features.proximity_image.raw_data, dtype=np.dtype('uint8'))
                array = np.reshape(array, (self.features.proximity_image.height, self.features.proximity_image.width, 4))
                array = array[:, :, :3]
                array = array[:, :, ::-1]

                self._last_proximity_image = pygame.surfarray.make_surface(array.swapaxes(0, 1))
            display.blit(self._last_proximity_image, (320, 0))

        # Render RGB camera image
        if self.features.rgb_image is not None:
            # Render image only if it has changed
            if self.features.rgb_image.frame_number > self._last_rgb_image_frame_number:
                self._last_rgb_image_frame_number = self.features.rgb_image.frame_number

                array = np.frombuffer(self.features.rgb_image.raw_data, dtype=np.dtype('uint8'))
                array = np.reshape(array, (self.features.rgb_image.height, self.features.rgb_image.width, 4))
                array = array[:, :, :3]
                array = array[:, :, ::-1]

                self._last_rgb_image = pygame.surfarray.make_surface(array.swapaxes(0, 1))
            display.blit(self._last_rgb_image, (480, 0))

        # Render LIDAR image
        if self.features.lidar_image is not None:
            dim = (320, 240)

            array = np.frombuffer(self.features.lidar_image.raw_data, dtype=np.dtype('f4'))
            array = np.reshape(array, (int(array.shape[0] / 3), 3))

            lidar_data = np.array(array[:, :2])
            lidar_data *= min(dim) / 100.0
            lidar_data += (0.5 * dim[0], 0.5 * dim[1])
            lidar_data = np.fabs(lidar_data)
            lidar_data = lidar_data.astype(np.int32)
            lidar_data = np.reshape(lidar_data, (-1, 2))

            lidar_img_size = (dim[0], dim[1], 3)
            lidar_img = np.zeros(lidar_img_size)
            lidar_img[tuple(lidar_data.T)] = (255, 255, 255)

            surface = pygame.surfarray.make_surface(lidar_img)

            display.blit(surface, (320, 120))
