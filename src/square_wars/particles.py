import pygame, random

from . import timer, common

class PixelParticle(pygame.sprite.Sprite):
    def __init__(self, position, layer, color, direction, life):
        super().__init__()
        self.layer = layer
        self.rect = pygame.FRect(position, (1, 1))
        self.direction = pygame.Vector2(direction)
        self.life_timer = timer.Timer(life)
        self.image = pygame.Surface((1, 1)).convert()
        self.image.fill(color)

    def visual_update(self):
        pass

    def update(self):
        self.rect.center += self.direction * common.dt
        self.life_timer.update()
        if not self.life_timer.time_left:
            self.kill()

def particle_splash(position, layer, color, count):
    for _ in range(count):
        x = position[0] + random.randint(-2, 2)
        y = position[1] + random.randint(-2, 2)
        direction = pygame.Vector2(0, 16)
        direction.rotate_ip(random.randint(0, 360))
        yield PixelParticle((x, y), layer, color, direction, 0.25)