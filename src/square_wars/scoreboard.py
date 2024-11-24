import pygame

from . import settings, timer, assets, chunky, common, utils


class ScoreBoard(pygame.sprite.Sprite):
    def __init__(self, gameplay_state, text=None):
        super().__init__()
        self.bg_image = utils.nine_slice(utils.get_sprite_sheet(assets.images["guiWoodBG"]), (64, 64))
        self.true_text = text
        title_image = assets.images["menu_title"]
        title_rect = title_image.get_rect()
        title_rect.centerx = self.bg_image.get_width() / 2
        title_rect.top = 1
        self.bg_image.blit(title_image, title_rect)
        self.image = self.bg_image.copy()
        self.inc_timer = timer.Timer(0.1)
        self.down_timer = timer.Timer(1)
        self.live_timer = timer.Timer(1)
        self.gameplay_state = gameplay_state
        self.rect = pygame.Rect(0, -64, 64, 64)
        self.leaving = False
        self.renderer = chunky.ChunkRenderer(chunky.parse_chunky_text(self.text), self.image.get_width() - 8)
        self.last_text = self.text

    @property
    def text(self):
        if self.true_text is not None:
            return self.true_text + '\n'
        team1_squares = self.gameplay_state.get_square_count(settings.TEAM_1)
        team1_kos = self.gameplay_state.get_ko_count(settings.TEAM_1)
        team2_squares = self.gameplay_state.get_square_count(settings.TEAM_2)
        team2_kos = self.gameplay_state.get_ko_count(settings.TEAM_2)
        return f"""
{settings.MR1_CHAR}={team1_squares - team1_kos:02d}
 {team1_squares:02d}{settings.TEAM1_TILE_CHAR}-{team1_kos:02d}{settings.TEAM1_KO_CHAR}
{settings.MR2_CHAR}={team2_squares - team2_kos:02d}
 {team2_squares:02d}{settings.TEAM2_TILE_CHAR}-{team2_kos:02d}{settings.TEAM2_KO_CHAR}
 """[1:]

    @property
    def done(self):
        return self.leaving and not self.down_timer.time_left

    def update(self):
        super().update()
        self.down_timer.update()
        self.live_timer.update()
        if not self.leaving:
            self.rect.top = pygame.math.lerp(-64, 0, 1 - self.down_timer.decimal_percent_left)
        else:
            self.rect.top = pygame.math.lerp(0, 64, 1 - self.down_timer.decimal_percent_left)
        if self.text != self.last_text:
            self.renderer.rechunk(chunky.parse_chunky_text(self.text))
        self.renderer.update()
        rect = self.renderer.image.get_bounding_rect()
        rect.centerx = self.image.get_rect().centerx
        rect.centery = self.image.get_rect().centerx
        rect.top = max(rect.top, 15)
        self.image = self.bg_image.copy()
        self.image.blit(self.renderer.image, rect)
        for event in common.events:
            if event.type in {pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN} and not self.live_timer.time_left:
                self.leaving = True
                self.down_timer.restart()