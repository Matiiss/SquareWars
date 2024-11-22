import pygame

from . import timer, common

class PixelParticle(pygame.sprite.Sprite):
    def __init__(self, position, color, direction, life, delta):
        super().__init__()
        self.rect = pygame.Rect(posirion, (1, 1))
        self.direction = pygame.Vector2(direction)
        self.life_timer = timer.Timer(life)
        self.image = pygame.Surface((1, 1)).convert()
        self.image.fill(color)

    def visual_update(self):
        pass

    def update(self):
        self.rect.center += self.direction * common.dt
        self.life_timer.update()
        return self.life_timer.time_left