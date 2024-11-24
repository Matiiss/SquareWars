import functools

import pygame


@functools.cache
def flip_surface(surface, flip_x, flip_y):
    if flip_x:
        surface = pygame.transform.flip(surface, True, False)
    if flip_y:
        surface = pygame.transform.flip(surface, False, True)
    return surface


def get_sprite_sheet(surface, size=(8, 8)):
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


def nine_slice(images, size):
    image = pygame.Surface(size).convert()
    image.fill("magenta")
    image.set_colorkey("magenta")
    rect = pygame.Rect(0, 0, *size)
    rects = [image.get_rect() for image in images]
    middle_rect = rect.copy()
    middle_rect.height -= rects[0].height + rects[6].height
    middle_rect.width -= rects[0].width + rects[2].width
    middle_rect.center = rect.center
    image.blit(images[0], (0, 0))
    image.blit(
        pygame.transform.scale(images[1], (middle_rect.width, rects[1].height)),
        (middle_rect.left, 0),
    )
    image.blit(images[2], (middle_rect.right, 0))
    image.blit(
        pygame.transform.scale(images[3], (rects[3].width, middle_rect.height)),
        (0, middle_rect.top),
    )
    image.blit(pygame.transform.scale(images[4], middle_rect.size), middle_rect.topleft)
    image.blit(
        pygame.transform.scale(images[5], (rects[5].width, middle_rect.height)),
        middle_rect.topright,
    )
    image.blit(images[6], (0, middle_rect.bottom))
    image.blit(
        pygame.transform.scale(images[7], (middle_rect.width, rects[7].height)),
        middle_rect.bottomleft,
    )

    image.blit(images[8], middle_rect.bottomright)
    return image
