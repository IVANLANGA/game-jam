import pygame
from settings import PLAYER_SPEED, DASH_SPEED, DASH_DURATION, DASH_COOLDOWN, TILE_SIZE, WIDTH, HEIGHT

PLAYER_DRAW_SIZE = TILE_SIZE * 2  # Add this line

class Player:
    def __init__(self, start_pos):
        self.pos = start_pos
        self.speed = PLAYER_SPEED
        self.dash_speed = DASH_SPEED
        self.dash_timer = 0
        self.dash_cooldown_timer = 0
        self.is_dashing = False

        # Animation setup
        self.sprite_sheet = pygame.image.load("assets/img/player.png").convert_alpha()
        self.frame_width = 64
        self.frame_height = 64
        self.frames_per_row = 9  # Only first 9 frames per row

        # Directions: 0=up, 1=left, 2=down, 3=right
        self.directions = ["up", "left", "down", "right"]
        self.row_map = {
            "up": 512,
            "left": 576,
            "down": 640,
            "right": 704,
        }
        self.animations = {}
        for dir_name in self.directions:
            y = self.row_map[dir_name]
            frames = []
            for i in range(self.frames_per_row):
                rect = pygame.Rect(i * self.frame_width, y, self.frame_width, self.frame_height)
                frame = self.sprite_sheet.subsurface(rect)
                # Scale to PLAYER_DRAW_SIZE (2x) instead of TILE_SIZE
                frame = pygame.transform.scale(frame, (PLAYER_DRAW_SIZE, PLAYER_DRAW_SIZE))
                frames.append(frame)
            self.animations[dir_name] = frames

        self.current_direction = "down"
        self.current_frame = 0
        self.frame_timer = 0
        self.frame_delay = 6  # Adjust for animation speed

        self.moving = False

    def handle_input(self, keys):
        move = pygame.Vector2(0, 0)
        if keys[pygame.K_LEFT]: move.x -= 1
        if keys[pygame.K_RIGHT]: move.x += 1
        if keys[pygame.K_UP]: move.y -= 1
        if keys[pygame.K_DOWN]: move.y += 1
        if move.length_squared() > 0:
            move = move.normalize()
            # Determine direction for animation
            if abs(move.x) > abs(move.y):
                self.current_direction = "right" if move.x > 0 else "left"
            else:
                self.current_direction = "down" if move.y > 0 else "up"
            self.moving = True
        else:
            self.moving = False
        return move

    def update(self, move, dash_pressed, dash_sound):
        if dash_pressed and self.dash_timer == 0 and self.dash_cooldown_timer == 0:
            self.is_dashing = True
            self.dash_timer = DASH_DURATION
            self.dash_cooldown_timer = DASH_COOLDOWN + DASH_DURATION
            dash_sound.play()

        if self.dash_timer > 0:
            current_speed = self.dash_speed
            self.dash_timer -= 1
            if self.dash_timer == 0:
                self.is_dashing = False
        else:
            current_speed = self.speed

        if self.dash_cooldown_timer > 0:
            self.dash_cooldown_timer -= 1

        self.pos += move * current_speed
        # Keep inside bounds (adjust for new draw size)
        self.pos.x = max(0, min(WIDTH - PLAYER_DRAW_SIZE, self.pos.x))
        self.pos.y = max(0, min(HEIGHT - PLAYER_DRAW_SIZE, self.pos.y))

        # Animation update
        if self.moving:
            self.frame_timer += 1
            if self.frame_timer >= self.frame_delay:
                self.frame_timer = 0
                self.current_frame = (self.current_frame + 1) % self.frames_per_row
        else:
            self.current_frame = 0  # Idle pose

    def draw(self, screen):
        frame = self.animations[self.current_direction][self.current_frame]
        screen.blit(frame, self.pos)
