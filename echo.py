import pygame
from collections import deque
from settings import TILE_SIZE, WHITE, BLACK, RED, YELLOW, GOOD_ECHO_LAG_FRAMES

class EchoManager:
    def __init__(self):
        self.echoes = []
        self.echo_frames = []
        self.recording = []

        self.echo_buffers = []

        self.good_echo_active = False
        self.good_echo_pos = None
        self.good_echo_timer = 0
        self.good_echo_current_duration = None
        self.good_echo_lag_queue = deque()

    def start_good_echo(self, duration_base, duration_increment):
        self.good_echo_active = True
        if self.good_echo_current_duration is None:
            self.good_echo_current_duration = duration_base
        self.good_echo_timer = self.good_echo_current_duration
        self.good_echo_current_duration += duration_increment

    def update(self, player_pos, screen):
        # Append player pos to recording
        self.recording.append(player_pos.copy())

        # Good echo lag logic
        if self.good_echo_active:
            self.good_echo_lag_queue.append(player_pos.copy())
            while len(self.good_echo_lag_queue) > GOOD_ECHO_LAG_FRAMES:
                self.good_echo_pos = self.good_echo_lag_queue.popleft()
        else:
            self.good_echo_lag_queue.clear()
            self.good_echo_pos = None

        # Echo buffer flashing before spawning actual echo
        new_buffers = []
        for buffer in self.echo_buffers:
            buffer['color_timer'] -= 1
            if buffer['color_timer'] <= 0:
                buffer['color_state'] = not buffer['color_state']
                buffer['color_timer'] = 15

            flash_color = WHITE if buffer['color_state'] else BLACK
            pygame.draw.rect(screen, flash_color, (*buffer['pos'], TILE_SIZE, TILE_SIZE))

            buffer['timer'] -= 1
            if buffer['timer'] <= 0:
                self.echoes.append(buffer['path'])
                self.echo_frames.append(0)
            else:
                new_buffers.append(buffer)
        self.echo_buffers = new_buffers

        # Update and draw echoes
        surviving_echoes = []
        surviving_frames = []
        for i in range(len(self.echoes)):
            path = self.echoes[i]
            if len(path) > 0:
                index = self.echo_frames[i] % len(path)
                echo_pos = path[index]

                if self.good_echo_active and self.good_echo_pos:
                    echo_rect = pygame.Rect(echo_pos.x, echo_pos.y, TILE_SIZE, TILE_SIZE)
                    good_echo_rect = pygame.Rect(self.good_echo_pos.x, self.good_echo_pos.y, TILE_SIZE, TILE_SIZE)
                    if echo_rect.colliderect(good_echo_rect):
                        continue

                pygame.draw.rect(screen, RED, (*echo_pos, TILE_SIZE, TILE_SIZE))

                surviving_echoes.append(path)
                surviving_frames.append(self.echo_frames[i] + 1)

        self.echoes = surviving_echoes
        self.echo_frames = surviving_frames

        # Good echo timer update
        if self.good_echo_active:
            self.good_echo_timer -= 1
            if self.good_echo_timer <= 0:
                self.good_echo_active = False
                self.good_echo_pos = None
                self.good_echo_lag_queue.clear()

        # Draw good echo
        if self.good_echo_active and self.good_echo_pos:
            pygame.draw.rect(screen, YELLOW, (*self.good_echo_pos, TILE_SIZE, TILE_SIZE))

    def add_echo_buffer(self, loop_path, pos):
        self.echo_buffers.append({
            'path': loop_path,
            'timer': 120,  # Could pass as param or use constant
            'color_state': True,
            'color_timer': 15,
            'pos': pos
        })

    def check_collision(self, player_pos):
        player_rect = pygame.Rect(player_pos.x, player_pos.y, TILE_SIZE, TILE_SIZE)
        for i, path in enumerate(self.echoes):
            index = self.echo_frames[i] % len(path)
            echo_pos = path[index]
            echo_rect = pygame.Rect(echo_pos.x, echo_pos.y, TILE_SIZE, TILE_SIZE)
            if player_rect.colliderect(echo_rect):
                return i + 1  # round number or echo index
        return None
