import pygame
from settings import PLAYER_SPEED, DASH_SPEED, DASH_DURATION, DASH_COOLDOWN, TILE_SIZE, WIDTH, HEIGHT

class Player:
    def __init__(self, start_pos):
        self.pos = start_pos
        self.speed = PLAYER_SPEED
        self.dash_speed = DASH_SPEED
        self.dash_timer = 0
        self.dash_cooldown_timer = 0
        self.is_dashing = False

    def handle_input(self, keys):
        move = pygame.Vector2(0, 0)
        if keys[pygame.K_LEFT]: move.x -= 1
        if keys[pygame.K_RIGHT]: move.x += 1
        if keys[pygame.K_UP]: move.y -= 1
        if keys[pygame.K_DOWN]: move.y += 1
        if move.length_squared() > 0:
            move = move.normalize()
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
        # Keep inside bounds
        self.pos.x = max(0, min(WIDTH - TILE_SIZE, self.pos.x))
        self.pos.y = max(0, min(HEIGHT - TILE_SIZE, self.pos.y))
