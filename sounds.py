import pygame

def load_sounds():
    collect_sound = pygame.mixer.Sound("assets/audio/collect.wav")
    dash_sound = pygame.mixer.Sound("assets/audio/dash.wav")
    gameover_sound = pygame.mixer.Sound("assets/audio/gameover.wav")
    return {
        "collect": collect_sound,
        "dash": dash_sound,
        "gameover": gameover_sound,
    }
