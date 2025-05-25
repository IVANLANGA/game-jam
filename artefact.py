import pygame
from utils import random_artefact_position
from settings import TILE_SIZE, GREEN

class Artefact:
    def __init__(self, start_pos):
        self.pos = start_pos
        self.collected = False

        # Load sprite sheet and extract frames
        self.sprite_sheet = pygame.image.load("assets/img/artefact.png").convert_alpha()
        self.frames = []
        for i in range(4):
            frame = self.sprite_sheet.subsurface(pygame.Rect(i * 16, 0, 16, 16))
            # Scale frame to TILE_SIZE if needed
            if TILE_SIZE != 16:
                frame = pygame.transform.scale(frame, (TILE_SIZE, TILE_SIZE))
            self.frames.append(frame)
        self.current_frame = 0
        self.frame_timer = 0
        self.frame_delay = 8  # Change frame every 8 ticks

    def draw(self, screen):
        if not self.collected:
            # Animate
            self.frame_timer += 1
            if self.frame_timer >= self.frame_delay:
                self.frame_timer = 0
                self.current_frame = (self.current_frame + 1) % len(self.frames)
            # Draw current frame
            screen.blit(self.frames[self.current_frame], self.pos)

    def check_collection(self, player_pos):
        if not self.collected:
            player_rect = pygame.Rect(player_pos.x, player_pos.y, TILE_SIZE, TILE_SIZE)
            artifact_rect = pygame.Rect(self.pos.x, self.pos.y, TILE_SIZE, TILE_SIZE)
            if player_rect.colliderect(artifact_rect):
                self.collected = True
                return True
        return False

    def respawn(self):
        self.pos = random_artefact_position(self.pos)
        self.collected = False
