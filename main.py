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

        while running:
            screen.fill(GRAY)
            keys = pygame.key.get_pressed()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    return

            move = player.handle_input(keys)
            dash_pressed = keys[pygame.K_z]
            freeze_pressed = keys[pygame.K_x]  # Add this line

            if sfx_on:
                player.update(move, dash_pressed, sounds["dash"])
            else:
                player.update(move, dash_pressed, type("Silent", (), {"play": lambda *a, **k: None})())

            # Freeze ability: if X is pressed, freeze bad echoes for 3 seconds (180 frames)
            if freeze_pressed and not echoes.freeze_bad_echoes:
                echoes.freeze_bad(180)  # 3 seconds at 60 FPS

            echoes.update(player.pos, screen)

            # Artefact logic
            artefact.draw(screen)
            if artefact.check_collection(player.pos):
                if sfx_on:
                    sounds["collect"].play()
                loop_path = echoes.recording + echoes.recording[::-1]
                echoes.add_echo_buffer(loop_path, loop_path[0])
                if round_number % 4 == 0:
                    echoes.start_good_echo(GOOD_ECHO_DURATION_BASE, GOOD_ECHO_DURATION_INCREMENT)
                echoes.recording = []
                round_number += 1
                artefact.respawn()

            # Check collisions with echoes
            collision_round = echoes.check_collision(player.pos)
            if collision_round is not None:
                print(f"Game Over! Touched echo from Round {collision_round}")
                running = False
                break

            # Draw player
            pygame.draw.rect(screen, BLUE, (*player.pos, TILE_SIZE, TILE_SIZE))

            # UI
            screen.blit(font.render(f"Round: {round_number}", True, WHITE), (10, 10))
            dash_status = "Ready" if player.dash_cooldown_timer == 0 else f"Wait ({player.dash_cooldown_timer // 60}s)"
            screen.blit(font.render(f"Dash: {dash_status}", True, WHITE), (10, 30))
            if echoes.good_echo_active:
                screen.blit(font.render("Good Echo Active!", True, YELLOW), (10, 50))

            pygame.display.flip()
            clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()
