import pygame

class SoundEffects:
    def __init__(self):
        pygame.mixer.init()
        self.step_sound = pygame.mixer.Sound(r"C:\Users\USER\Desktop\bootcamp\CTD\from smuel\CTD25_Solutions\KungFu Chess\music\step.mp3")
        self.error_sound = pygame.mixer.Sound(r"C:\Users\USER\Desktop\bootcamp\CTD\from smuel\CTD25_Solutions\KungFu Chess\music\error.mp3")
        self.fail_sound = pygame.mixer.Sound(r"C:\Users\USER\Desktop\bootcamp\CTD\from smuel\CTD25_Solutions\KungFu Chess\music\fail.mp3")
        self.capture_sound = pygame.mixer.Sound(r"C:\Users\USER\Desktop\bootcamp\CTD\from smuel\CTD25_Solutions\KungFu Chess\music\capture.mp3")

    def on_piece_moved(self, data):
        self.step_sound.play()

    def on_piece_captured(self, data):
        self.capture_sound.play()

    def on_move_rejected(self, data):
        self.error_sound.play()
    def on_piece_jump(self, data):
        self.fail_sound.play()
