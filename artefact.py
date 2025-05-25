import pygame
from utils import random_artefact_position
from settings import TILE_SIZE, GREEN

class Artefact:
    def __init__(self, start_pos):
        self.pos = start_pos
        self.collected = False

    def draw(self, screen):
        if not self.collected:
            pygame.draw.rect(screen, GREEN, (*self.pos, TILE_SIZE, TILE_SIZE))

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
