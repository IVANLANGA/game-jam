import pygame
from settings import *
from player import Player
from artefact import Artefact
from echo import EchoManager
from sounds import load_sounds

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Echo Dash")
    pygame.mixer.init()

    font = pygame.font.SysFont("consolas", FONT_SIZE)

    sounds = load_sounds()
    pygame.mixer.music.load("assets/audio/background.ogg")
    pygame.mixer.music.play(-1)

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

        move = player.handle_input(keys)
        dash_pressed = keys[pygame.K_z]
        player.update(move, dash_pressed, sounds["dash"])

        echoes.update(player.pos, screen)

        # Artefact logic
        artefact.draw(screen)
        if artefact.check_collection(player.pos):
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
