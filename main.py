import pygame
from settings import *
from player import Player
from artefact import Artefact
from echo import EchoManager
from sounds import load_sounds

def draw_menu(screen, font, selected_idx, options, sfx_on, music_on):
    screen.fill(GRAY)
    title = font.render("Echo Dash", True, YELLOW)
    screen.blit(title, (WIDTH // 2 - title.get_width() // 2, HEIGHT // 4))
    for i, option in enumerate(options):
        color = WHITE if i == selected_idx else BLUE
        text = font.render(option, True, color)
        screen.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2 + i * 40))
    # Show SFX/Music status
    sfx_text = font.render(f"SFX: {'On' if sfx_on else 'Off'}", True, WHITE)
    music_text = font.render(f"Music: {'On' if music_on else 'Off'}", True, WHITE)
    screen.blit(sfx_text, (WIDTH // 2 - sfx_text.get_width() // 2, HEIGHT // 2 + len(options) * 40 + 20))
    screen.blit(music_text, (WIDTH // 2 - music_text.get_width() // 2, HEIGHT // 2 + len(options) * 40 + 50))
    pygame.display.flip()

def menu_loop(screen, font, sfx_on, music_on):
    options = ["Start Game", "Toggle SFX", "Toggle Music", "Quit"]
    selected_idx = 0
    while True:
        draw_menu(screen, font, selected_idx, options, sfx_on, music_on)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit", sfx_on, music_on
            if event.type == pygame.KEYDOWN:
                if event.key in [pygame.K_UP, pygame.K_w]:
                    selected_idx = (selected_idx - 1) % len(options)
                elif event.key in [pygame.K_DOWN, pygame.K_s]:
                    selected_idx = (selected_idx + 1) % len(options)
                elif event.key in [pygame.K_RETURN, pygame.K_SPACE]:
                    choice = options[selected_idx].lower().replace(" ", "_")
                    if choice == "toggle_sfx":
                        sfx_on = not sfx_on
                    elif choice == "toggle_music":
                        music_on = not music_on
                        if music_on:
                            pygame.mixer.music.unpause()
                        else:
                            pygame.mixer.music.pause()
                    else:
                        return choice, sfx_on, music_on
        pygame.time.wait(100)

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Echo Dash")
    pygame.mixer.init()

    font = pygame.font.SysFont("consolas", FONT_SIZE)

    sounds = load_sounds()
    pygame.mixer.music.load("assets/audio/background.ogg")
    pygame.mixer.music.play(-1)

    sfx_on = True
    music_on = True

    while True:
        menu_action, sfx_on, music_on = menu_loop(screen, font, sfx_on, music_on)
        if menu_action == "quit":
            break
        if not music_on:
            pygame.mixer.music.pause()
        else:
            pygame.mixer.music.unpause()

        player = Player(pygame.Vector2(5 * TILE_SIZE, 5 * TILE_SIZE))
        artefact = Artefact(pygame.Vector2(5 * TILE_SIZE, 8 * TILE_SIZE))
        echoes = EchoManager()

        round_number = 1
        running = True
        clock = pygame.time.Clock()

        artefact_count = 0
        freeze_cost = 3

        game_state = "playing"
        game_over_anim = None
        game_over_timer = 0

        
        good_echo_spawn_interval = 4  # Initial interval in rounds
        good_echo_next_spawn = good_echo_spawn_interval

        while running:
            if game_state == "playing":
                screen.fill(GRAY)
                keys = pygame.key.get_pressed()

                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False
                        return

                move = player.handle_input(keys)
                dash_pressed = keys[pygame.K_z]
                freeze_pressed = keys[pygame.K_x]

                if sfx_on:
                    player.update(move, dash_pressed, sounds["dash"])
                else:
                    player.update(move, dash_pressed, type("Silent", (), {"play": lambda *a, **k: None})())

                # Freeze ability: costs artefacts, cost increases after each use
                if freeze_pressed and not echoes.freeze_bad_echoes and artefact_count >= freeze_cost:
                    artefact_count -= freeze_cost
                    echoes.freeze_bad(180)  # 3 seconds at 60 FPS
                    freeze_cost += 1

                echoes.update(player.pos, screen)

                # Artefact logic
                artefact.draw(screen)
                if artefact.check_collection(player.pos):
                    if sfx_on:
                        sounds["collect"].play()
                    loop_path = echoes.recording + echoes.recording[::-1]
                    echoes.add_echo_buffer(loop_path, loop_path[0])
                    # Good echo spawns every good_echo_spawn_interval rounds, then interval increases by 2
                    if round_number == good_echo_next_spawn:
                        echoes.start_good_echo(GOOD_ECHO_DURATION_BASE, GOOD_ECHO_DURATION_INCREMENT)
                        good_echo_spawn_interval += 2
                        good_echo_next_spawn += good_echo_spawn_interval
                    echoes.recording = []
                    round_number += 1
                    artefact.respawn()
                    artefact_count += 1  # Increment artefact count on collection

                # Check collisions with echoes
                collision_round = echoes.check_collision(player.pos)
                if collision_round is not None:
                    print(f"Game Over! Touched echo from Round {collision_round}")
                    pygame.mixer.music.stop()
                    if sfx_on:
                        sounds["gameover"].play()
                    game_over_anim = GameOverAnimation(screen)
                    game_over_timer = 0
                    game_state = "game_over"
                    continue

               #UI
                player.draw(screen)

               
                screen.blit(font.render(f"Round: {round_number}", True, WHITE), (10, 10))
                dash_status = "Ready" if player.dash_cooldown_timer == 0 else f"Wait ({player.dash_cooldown_timer // 60}s)"
                screen.blit(font.render(f"Dash: {dash_status}", True, WHITE), (10, 30))
                screen.blit(font.render(f"Gems: {artefact_count}", True, GREEN), (10, 50))
                screen.blit(font.render(f"Freeze Cost: {freeze_cost}", True, BLUE), (10, 70))
                if echoes.good_echo_active:
                    screen.blit(font.render("Good Echo Active!", True, YELLOW), (10, 90))
                if echoes.freeze_bad_echoes:
                    screen.blit(font.render("Freeze Active!", True, BLUE), (10, 110))

                pygame.display.flip()
                clock.tick(60)
            elif game_state == "game_over":
                screen.fill(BLACK)
                if game_over_anim:
                    game_over_anim.update()
                    game_over_anim.draw()
             
             
                text = font.render("Game Over!", True, RED)
                screen.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2 + 80))
                pygame.display.flip()
                clock.tick(60)
                game_over_timer += 1
                # Wait for animation to finish, then pause a bit, then return to menu
                if game_over_anim and game_over_anim.finished and game_over_timer > 60:
                    pygame.time.wait(1200)  # 1.2 second pause after animation
                    pygame.mixer.music.play(-1)
                    running = False
                    break

    pygame.quit()

class GameOverAnimation:
    def __init__(self, screen):
        self.screen = screen
        self.sprite_sheet = pygame.image.load("assets/img/player.png").convert_alpha()
        self.frame_width = 64
        self.frame_height = 64
        self.num_frames = 6
        self.frames = []
        y = 1280  # Row 21
        scale = 2  # Scale up for visibility (optional)
        for i in range(self.num_frames):
            rect = pygame.Rect(i * self.frame_width, y, self.frame_width, self.frame_height)
            frame = self.sprite_sheet.subsurface(rect)
            frame = pygame.transform.scale(frame, (self.frame_width * scale, self.frame_height * scale))
            self.frames.append(frame)
        self.current_frame = 0
        self.frame_delay = 8  # Frames to wait before advancing
        self.frame_timer = 0
        self.finished = False
        self.center_x = (WIDTH // 2) - (self.frame_width * scale // 2)
        self.center_y = (HEIGHT // 2) - (self.frame_height * scale // 2)

    def update(self):
        if not self.finished:
            self.frame_timer += 1
            if self.frame_timer >= self.frame_delay:
                self.frame_timer = 0
                self.current_frame += 1
                if self.current_frame >= self.num_frames:
                    self.current_frame = self.num_frames - 1
                    self.finished = True

    def draw(self):
        self.screen.blit(self.frames[self.current_frame], (self.center_x, self.center_y))

if __name__ == "__main__":
    main()
