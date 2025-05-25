import random
import pygame
from settings import WIDTH, HEIGHT, TILE_SIZE

def random_artefact_position(artefact_pos):
    while True:
        grid_x = random.randint(1, (WIDTH - TILE_SIZE) // TILE_SIZE - 1)
        grid_y = random.randint(1, (HEIGHT - TILE_SIZE) // TILE_SIZE - 1)
        new_pos = pygame.Vector2(grid_x * TILE_SIZE, grid_y * TILE_SIZE)
        if new_pos.distance_to(artefact_pos) > 3 * TILE_SIZE:
            return new_pos
