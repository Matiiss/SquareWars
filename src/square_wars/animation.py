import functools

import pygame

from . import common


@functools.cache
def flip_surface(surface, flip_x, flip_y):
    if flip_x:
        surface = pygame.transform.flip(surface, True, False)
    if flip_y:
        surface = pygame.transform.flip(surface, False, True)
    return surface


def get_spritesheet(surface, size=(8, 8)):
    rect = pygame.Rect(0, 0, size[0], size[1])
    size_rect = surface.get_rect()
    images = []
    while True:
        images.append(surface.subsurface(rect).copy())
        rect.left += size[0]
        if not size_rect.contains(rect):
            rect.left = 0
            rect.top += size[1]
        if not size_rect.contains(rect):
            break
    return images


class Animation:
    def __init__(self, frames, speed=0.2, flip_x=False, flip_y=False):
        self.frames = list(frames)
        self.time = 0
        self.speed = speed
        self.flip_x = flip_x
        self.flip_y = flip_y

    def update(self):
        self.time += common.dt

    def restart(self):
        self.time = 0

    @property
    def image(self):
        image = self.frames[round(self.time / self.speed) % len(self.frames)]
        return flip_surface(image, self.flip_x, self.flip_y)


class NoLoopAnimation:
    def __init__(self, frames, speed=0.2, flip_x=False, flip_y=False):
        self.frames = list(frames)
        self.time = 0
        self.speed = speed
        self.flip_x = flip_x
        self.flip_y = flip_y

    def update(self):
        self.time += common.dt

    def restart(self):
        self.time = 0

    def done(self):
        return min(round(self.time / self.speed), len(self.frames) - 1) == len(self.frames) - 1

    @property
    def image(self):
        frame_index = min(round(self.time / self.speed), len(self.frames) - 1)
        return flip_surface(self.frames[frame_index], self.flip_x, self.flip_y)


class SingleAnimation:
    def __init__(self, surface, flip_x=False, flip_y=False):
        self.surface = surface
        self.flip_x = flip_x
        self.flip_y = flip_y

    def update(self):
        pass

    def restart(self):
        pass

    @property
    def image(self):
        return flip_surface(self.surface, self.flip_x, self.flip_y)
