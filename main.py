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
YELLOW = (255, 255, 0)
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
echoes = []           # List of paths (list of Vector2)
echo_frames = []      # Current frame index in each echo path
recording = []        # Current round's player path

# Good Echo
good_echo_active = False
good_echo_pos = None
good_echo_timer = 0
GOOD_ECHO_LAG_FRAMES = 80  # increased lag for more delay
GOOD_ECHO_DURATION_FRAMES = 20 * 60  # 20 seconds at 60 FPS
good_echo_lag_queue = deque()  # store player positions for lagging

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

    # Update good echo lag queue if active
    if good_echo_active:
        good_echo_lag_queue.append(player_pos.copy())
        # Maintain lag queue size
        while len(good_echo_lag_queue) > GOOD_ECHO_LAG_FRAMES:
            good_echo_pos = good_echo_lag_queue.popleft()
    else:
        good_echo_lag_queue.clear()
        good_echo_pos = None

    # Draw artifact and check collection
    if not collected:
        pygame.draw.rect(screen, GREEN, (*artifact_pos, TILE_SIZE, TILE_SIZE))
        if pygame.Rect(player_pos.x, player_pos.y, TILE_SIZE, TILE_SIZE).colliderect(
            pygame.Rect(artifact_pos.x, artifact_pos.y, TILE_SIZE, TILE_SIZE)
        ):
            collected = True
            # Create a full back-and-forth loop path for bad echo
            loop_path = recording + recording[::-1]
            echoes.append(loop_path)
            echo_frames.append(0)

            # Every 4th round, activate good echo
            if round_number % 4 == 0:
                good_echo_active = True
                good_echo_timer = GOOD_ECHO_DURATION_FRAMES
                # Do NOT reset good_echo_pos here, lag queue will handle smooth follow

            recording = []
            round_number += 1
            artifact_pos = random_artifact_position()

    # Update and draw echoes (bad echoes)
    surviving_echoes = []
    surviving_frames = []
    for i in range(len(echoes)):
        path = echoes[i]
        if len(path) > 0:
            index = echo_frames[i] % len(path)  # loop forever
            echo_pos = path[index]

            # If good echo touches this echo, destroy it
            if good_echo_active and good_echo_pos:
                echo_rect = pygame.Rect(echo_pos.x, echo_pos.y, TILE_SIZE, TILE_SIZE)
                good_echo_rect = pygame.Rect(good_echo_pos.x, good_echo_pos.y, TILE_SIZE, TILE_SIZE)
                if echo_rect.colliderect(good_echo_rect):
                    # Destroy this echo (skip adding it to surviving list)
                    continue

            pygame.draw.rect(screen, RED, (*echo_pos, TILE_SIZE, TILE_SIZE))

            # Collision with player
            if pygame.Rect(player_pos.x, player_pos.y, TILE_SIZE, TILE_SIZE).colliderect(
                pygame.Rect(echo_pos.x, echo_pos.y, TILE_SIZE, TILE_SIZE)
            ):
                print(f"Game Over! Touched echo from Round {i + 1}")
                running = False

            echo_frames[i] += 1
            surviving_echoes.append(path)
            surviving_frames.append(echo_frames[i])

    echoes = surviving_echoes
    echo_frames = surviving_frames

    # Update good echo timer and deactivate if time's up
    if good_echo_active:
        good_echo_timer -= 1
        if good_echo_timer <= 0:
            good_echo_active = False
            good_echo_pos = None
            good_echo_lag_queue.clear()

    # Draw good echo as single yellow block if active
    if good_echo_active and good_echo_pos:
        pygame.draw.rect(screen, YELLOW, (*good_echo_pos, TILE_SIZE, TILE_SIZE))

    # Draw player
    pygame.draw.rect(screen, BLUE, (*player_pos, TILE_SIZE, TILE_SIZE))

    # Reset artifact flag after drawing and logic
    if collected:
        collected = False

    # UI
    screen.blit(font.render(f"Round: {round_number}", True, WHITE), (10, 10))
    screen.blit(font.render(f"Dash: {'Ready' if dash_timer == 0 else 'Cooling'}", True, WHITE), (10, 30))
    if good_echo_active:
        screen.blit(font.render("Good Echo Active!", True, YELLOW), (10, 50))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
