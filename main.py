import pygame
from collections import deque
import random
# Scythe_x_Kabayama_Time_goes_on.ogg
# Init
pygame.init()
WIDTH, HEIGHT = 640, 480
TILE_SIZE = 32
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Echo Dash")

pygame.mixer.init()
collect_sound = pygame.mixer.Sound("assets/audio/collect.wav")
dash_sound = pygame.mixer.Sound("assets/audio/dash.wav")
# slowmo_sound = pygame.mixer.Sound("sounds/slowmo.wav")
# gameover_sound = pygame.mixer.Sound("sounds/gameover.wav")

# Background music
pygame.mixer.music.load("assets/audio/background.ogg")
pygame.mixer.music.play(-1)  # Loop indefinitely

# Clock & Colors
clock = pygame.time.Clock()
WHITE = (255, 255, 255)
BLUE = (50, 100, 255)
GREEN = (50, 255, 100)
RED = (255, 50, 50)
YELLOW = (255, 255, 0)
BLACK = (0, 0, 0)
GRAY = (30, 30, 30)

# Font
font = pygame.font.SysFont("consolas", 20)

# Player
player_pos = pygame.Vector2(5 * TILE_SIZE, 5 * TILE_SIZE)
player_speed = 2.5
dash_speed = 5
DASH_DURATION = 60            # 1 second at 60 FPS
DASH_COOLDOWN = 180           # 4 seconds cooldown
dash_timer = 0
dash_cooldown_timer = 0
is_dashing = False

# Echoes
echoes = []
echo_frames = []
recording = []

# Good Echo
good_echo_active = False
good_echo_pos = None
good_echo_timer = 0
GOOD_ECHO_LAG_FRAMES = 80
GOOD_ECHO_DURATION_BASE = 10 * 60  # start at 10 seconds
good_echo_duration_increment = 2 * 60
good_echo_current_duration = GOOD_ECHO_DURATION_BASE
good_echo_lag_queue = deque()

# Artifact
def random_artifact_position():
    while True:
        grid_x = random.randint(1, (WIDTH - TILE_SIZE) // TILE_SIZE - 1)
        grid_y = random.randint(1, (HEIGHT - TILE_SIZE) // TILE_SIZE - 1)
        new_pos = pygame.Vector2(grid_x * TILE_SIZE, grid_y * TILE_SIZE)
        if new_pos.distance_to(artifact_pos) > 3 * TILE_SIZE:
            return new_pos

artifact_pos = pygame.Vector2(5 * TILE_SIZE, 8 * TILE_SIZE)
collected = False

# --- New variables for echo spawn buffer ---
ECHO_BUFFER_TIME = 120  # 2 seconds at 60 FPS
echo_buffers = []       # List of dicts: {'path', 'timer', 'color_state', 'color_timer', 'pos'}

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

    # Dash logic
    if keys[pygame.K_z] and dash_timer == 0 and dash_cooldown_timer == 0:
        is_dashing = True
        dash_timer = DASH_DURATION
        dash_cooldown_timer = DASH_COOLDOWN + DASH_DURATION
        dash_sound.play()  # <-- Play dash sound here

    if dash_timer > 0:
        current_speed = dash_speed
        dash_timer -= 1
        if dash_timer == 0:
            is_dashing = False
    else:
        current_speed = player_speed

    if dash_cooldown_timer > 0:
        dash_cooldown_timer -= 1

    # Update player position
    player_pos += move * current_speed

    # Keep player inside screen bounds
    player_pos.x = max(0, min(WIDTH - TILE_SIZE, player_pos.x))
    player_pos.y = max(0, min(HEIGHT - TILE_SIZE, player_pos.y))

    recording.append(player_pos.copy())

    # Good echo lag logic (unchanged)
    if good_echo_active:
        good_echo_lag_queue.append(player_pos.copy())
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
            collect_sound.play()  # <-- Play collect sound here

            # --- Instead of adding echo directly, add to buffer ---
            loop_path = recording + recording[::-1]
            echo_buffers.append({
                'path': loop_path,
                'timer': ECHO_BUFFER_TIME,
                'color_state': True,
                'color_timer': 15,  # toggle color every 15 frames (~0.25s)
                'pos': loop_path[0]
            })

            if round_number % 4 == 0:
                good_echo_active = True
                good_echo_timer = good_echo_current_duration
                good_echo_current_duration += good_echo_duration_increment

            recording = []
            round_number += 1
            artifact_pos = random_artifact_position()

    # --- Handle echo buffers: flashing indicator before spawning actual echo ---
    new_echo_buffers = []
    for buffer in echo_buffers:
        # Update flashing color timer
        buffer['color_timer'] -= 1
        if buffer['color_timer'] <= 0:
            buffer['color_state'] = not buffer['color_state']
            buffer['color_timer'] = 15

        # Draw flashing rect at spawn position
        flash_color = WHITE if buffer['color_state'] else BLACK
        pygame.draw.rect(screen, flash_color, (*buffer['pos'], TILE_SIZE, TILE_SIZE))

        # Countdown timer
        buffer['timer'] -= 1
        if buffer['timer'] <= 0:
            # Spawn the actual echo after buffer time
            echoes.append(buffer['path'])
            echo_frames.append(0)
        else:
            new_echo_buffers.append(buffer)
    echo_buffers = new_echo_buffers

    # Update and draw echoes
    surviving_echoes = []
    surviving_frames = []
    for i in range(len(echoes)):
        path = echoes[i]
        if len(path) > 0:
            index = echo_frames[i] % len(path)
            echo_pos = path[index]

            if good_echo_active and good_echo_pos:
                echo_rect = pygame.Rect(echo_pos.x, echo_pos.y, TILE_SIZE, TILE_SIZE)
                good_echo_rect = pygame.Rect(good_echo_pos.x, good_echo_pos.y, TILE_SIZE, TILE_SIZE)
                if echo_rect.colliderect(good_echo_rect):
                    continue

            pygame.draw.rect(screen, RED, (*echo_pos, TILE_SIZE, TILE_SIZE))

            if pygame.Rect(player_pos.x, player_pos.y, TILE_SIZE, TILE_SIZE).colliderect(
                pygame.Rect(echo_pos.x, echo_pos.y, TILE_SIZE, TILE_SIZE)
            ):
                print(f"Game Over! Touched echo from Round {i + 1}")
                # gameover_sound.play()  # <-- optionally play game over sound here
                running = False

            echo_frames[i] += 1
            surviving_echoes.append(path)
            surviving_frames.append(echo_frames[i])

    echoes = surviving_echoes
    echo_frames = surviving_frames

    # Good echo timer update (unchanged)
    if good_echo_active:
        good_echo_timer -= 1
        if good_echo_timer <= 0:
            good_echo_active = False
            good_echo_pos = None
            good_echo_lag_queue.clear()

    # Draw good echo if active
    if good_echo_active and good_echo_pos:
        pygame.draw.rect(screen, YELLOW, (*good_echo_pos, TILE_SIZE, TILE_SIZE))

    # Draw player
    pygame.draw.rect(screen, BLUE, (*player_pos, TILE_SIZE, TILE_SIZE))

    if collected:
        collected = False

    # UI
    screen.blit(font.render(f"Round: {round_number}", True, WHITE), (10, 10))
    dash_status = "Ready" if dash_cooldown_timer == 0 else f"Wait ({dash_cooldown_timer // 60}s)"
    screen.blit(font.render(f"Dash: {dash_status}", True, WHITE), (10, 30))
    if good_echo_active:
        screen.blit(font.render("Good Echo Active!", True, YELLOW), (10, 50))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
