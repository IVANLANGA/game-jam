import pygame
from collections import deque

# Initialize
pygame.init()
WIDTH, HEIGHT = 640, 480
TILE_SIZE = 32
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Echo Dash")

# Clock and Colors
clock = pygame.time.Clock()
WHITE = (255, 255, 255)
BLUE = (50, 100, 255)
GREEN = (50, 255, 100)
RED = (255, 50, 50)
GRAY = (30, 30, 30)

# Player settings
player_pos = pygame.Vector2(5 * TILE_SIZE, 5 * TILE_SIZE)
player_speed = 2
dash_speed = 6
dash_cooldown = 60  # frames
dash_timer = 0

# Echo replay data
echo_path = deque()
echo_pos = None
echo_frame = 0

# Artifact
artifact_pos = pygame.Vector2(12 * TILE_SIZE, 8 * TILE_SIZE)
collected = False

# Fonts
font = pygame.font.SysFont("consolas", 20)

# Game State
running = True
recording = []
game_phase = 1  # Phase 1: playing, Phase 2+: echo mode

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

    player_pos += move * current_speed
    if dash_timer > 0:
        dash_timer -= 1

    # Draw player
    pygame.draw.rect(screen, BLUE, (*player_pos, TILE_SIZE, TILE_SIZE))

    # Record movement
    recording.append(player_pos.copy())

    # Draw artifact
    if not collected:
        pygame.draw.rect(screen, GREEN, (*artifact_pos, TILE_SIZE, TILE_SIZE))
        if pygame.Rect(player_pos.x, player_pos.y, TILE_SIZE, TILE_SIZE).colliderect(
            pygame.Rect(artifact_pos.x, artifact_pos.y, TILE_SIZE, TILE_SIZE)
        ):
            collected = True
            echo_path = deque(recording)  # save for ghost
            echo_frame = 0
            game_phase += 1
            recording = []

    # Echo ghost
    if game_phase > 1 and echo_path:
        if echo_frame < len(echo_path):
            echo_pos = echo_path[echo_frame]
            pygame.draw.rect(screen, RED, (*echo_pos, TILE_SIZE, TILE_SIZE))
            if pygame.Rect(player_pos.x, player_pos.y, TILE_SIZE, TILE_SIZE).colliderect(
                pygame.Rect(echo_pos.x, echo_pos.y, TILE_SIZE, TILE_SIZE)
            ):
                print("Game Over! You touched your echo.")
                running = False
            echo_frame += 1

    # UI
    dash_text = f"Dash: {'Ready' if dash_timer == 0 else 'Cooling'}"
    screen.blit(font.render(dash_text, True, WHITE), (10, 10))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
