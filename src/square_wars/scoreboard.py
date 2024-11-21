import pygame

from . import settings, timer, animation, assets, chunky

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


class ScoreBoard(pygame.sprite.Sprite):
    def __init__(self, gameplay_state):
        super().__init__()
        self.bg_image = nine_slice(animation.get_spritesheet(assets.images["guiWoodBG"]), (64, 64))
        self.image = self.bg_image.copy()
        self.inc_timer = timer.Timer(0.1)
        self.down_timer = timer.Timer(1)
        self.gameplay_state = gameplay_state
        self.rect = pygame.Rect(0, 0, 64, 64)
        self.renderer = chunky.ChunkRenderer(chunky.parse_chunky_text(self.text), self.image.get_width() - 8)
        self.last_text = self.text

    @property
    def text(self):
        team1_squares = self.gameplay_state.get_square_count(settings.TEAM_1)
        team1_kos = self.gameplay_state.get_ko_count(settings.TEAM_1)
        team2_squares = self.gameplay_state.get_square_count(settings.TEAM_2)
        team2_kos = self.gameplay_state.get_ko_count(settings.TEAM_2)
        return f"""
{settings.MR1_CHAR}={team1_squares + team1_kos}
 {team1_squares}x{settings.TEAM1_TILE_CHAR} {team1_kos}x{settings.TEAM1_KO_CHAR}
{settings.MR2_CHAR}={team2_squares + team2_kos}
 {team1_squares}x{settings.TEAM2_TILE_CHAR} {team1_kos}x{settings.TEAM2_KO_CHAR}
        """[1:]

    def update(self):
        super().update()
        if self.text != self.last_text:
            self.renderer.rechunk(chunky.parse_chunky_text(self.text))
        self.renderer.update()
        rect = self.renderer.image.get_rect()
        rect.center = self.image.get_rect().center
        self.image = self.bg_image.copy()
        self.image.blit(self.renderer.image, rect)