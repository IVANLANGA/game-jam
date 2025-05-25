import pygame
from collections import deque
import random

# Init
pygame.init()
WIDTH, HEIGHT = 640, 480
TILE_SIZE = 32
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Echo Dash")

# Clock & Colors
clock = pygame.time.Clock()
WHITE = (255, 255, 255)
BLUE = (50, 100, 255)
GREEN = (50, 255, 100)
RED = (255, 50, 50)
GRAY = (30, 30, 30)

# Font
font = pygame.font.SysFont("consolas", 20)

# Player
player_pos = pygame.Vector2(5 * TILE_SIZE, 5 * TILE_SIZE)
player_speed = 2
dash_speed = 6
dash_cooldown = 60
dash_timer = 0

# Echoes
echoes = []           # List of deque paths
echo_frames = []      # Current frame index in each echo path
recording = []        # Current round's player path

# Artifact
def random_artifact_position():
    grid_x = random.randint(1, (WIDTH - TILE_SIZE) // TILE_SIZE - 1)
    grid_y = random.randint(1, (HEIGHT - TILE_SIZE) // TILE_SIZE - 1)
    return pygame.Vector2(grid_x * TILE_SIZE, grid_y * TILE_SIZE)

artifact_pos = random_artifact_position()
collected = False

# Game state
round_number = 1
running = True

# Loop
while running:
    screen.fill(GRAY)
    keys = pygame.key.get_pressed()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Movement
    move = pygame.Vector2(0, 0)
    if keys[pygame.K_LEFT]: move.x -= 1
    if keys[pygame.K_RIGHT]: move.x += 1
    if keys[pygame.K_UP]: move.y -= 1
    if keys[pygame.K_DOWN]: move.y += 1
    if move.length_squared() > 0:
        move = move.normalize()

    # Dash
    current_speed = player_speed
    if keys[pygame.K_z] and dash_timer == 0:
        current_speed = dash_speed
        dash_timer = dash_cooldown
    if dash_timer > 0:
        dash_timer -= 1

    # Update player
    player_pos += move * current_speed
    recording.append(player_pos.copy())

    # Draw artifact and check collection
    if not collected:
        pygame.draw.rect(screen, GREEN, (*artifact_pos, TILE_SIZE, TILE_SIZE))
        if pygame.Rect(player_pos.x, player_pos.y, TILE_SIZE, TILE_SIZE).colliderect(
            pygame.Rect(artifact_pos.x, artifact_pos.y, TILE_SIZE, TILE_SIZE)
        ):
            collected = True
            # Create a full back-and-forth loop path
            loop_path = recording + recording[::-1]
            echoes.append(loop_path)
            echo_frames.append(0)

            recording = []
            round_number += 1
            artifact_pos = random_artifact_position()

    # Draw echoes
    for i in range(len(echoes)):
        path = echoes[i]
        if len(path) > 0:
            index = echo_frames[i] % len(path)  # loop forever
            echo_pos = path[index]
            pygame.draw.rect(screen, RED, (*echo_pos, TILE_SIZE, TILE_SIZE))

            # Collision with player
            if pygame.Rect(player_pos.x, player_pos.y, TILE_SIZE, TILE_SIZE).colliderect(
                pygame.Rect(echo_pos.x, echo_pos.y, TILE_SIZE, TILE_SIZE)
            ):
                print(f"Game Over! Touched echo from Round {i + 1}")
                running = False

            echo_frames[i] += 1

    # Draw player
    pygame.draw.rect(screen, BLUE, (*player_pos, TILE_SIZE, TILE_SIZE))

    # Reset artifact flag after drawing and logic
    if collected:
        collected = False

    # UI
    screen.blit(font.render(f"Round: {round_number}", True, WHITE), (10, 10))
    screen.blit(font.render(f"Dash: {'Ready' if dash_timer == 0 else 'Cooling'}", True, WHITE), (10, 30))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
