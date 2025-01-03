from typing import Any

import pygame
import random
import math
import pygame._sdl2 as pg_sdl2  # noqa

from .. import common, assets, ui, utils, easings, timer, settings

from . import transition, gameplay


class Cloud(pygame.sprite.Sprite):
    SPEED = 8

    def __init__(self, position):
        super().__init__()
        self.image = random.choice(utils.get_sprite_sheet(assets.images["clouds"], (24, 16)))
        self.rect = pygame.FRect(position, (24, 16))
        self.ui = None

    def set_ui(self, ui):
        self.ui = ui

    def update(self):
        self.rect.x += self.SPEED * common.dt
        if self.rect.x > 64:
            self.rect.right = 0


class Smoke(pygame.sprite.Sprite):
    SPEED = 15

    def __init__(self, position):
        super().__init__()
        self.radius = random.randint(1, 2)
        self.image = pygame.Surface((self.radius * 2, self.radius * 2)).convert_alpha()
        self.image.fill((0, 0, 0, 0))
        pygame.draw.circle(self.image, "#5d5d5d", (self.radius, self.radius), self.radius)
        self.direction = pygame.Vector2(0, -self.SPEED)
        self.rect = pygame.FRect(self.image.get_rect(center=position))
        self.x = self.rect.x
        self.age = random.random() * 10

    def update(self):
        self.age += common.dt
        self.rect.top -= self.SPEED * common.dt
        self.rect.x = math.sin(self.age * 2) * 3 + self.x

        if self.rect.bottom < 0:
            self.kill()


class MainMenu:
    caption_string = "Main Menu"
    day_color = pygame.color.Color("#0098dc")
    night_color = pygame.color.Color("#1a1932")
    day_window_color = pygame.color.Color("#131313")
    night_window_color = pygame.color.Color("#ffeb57")
    # that's right - I hardcoded individual pixel coordinates
    window_coordinates = (
        (5, 42),
        (4, 43),
        (5, 43),
        (6, 43),
        (6, 46),
        (7, 46),
        (6, 47),
        (7, 47),
        (59, 56),
        (58, 57),
        (59, 57),
        (60, 57),
        (60, 60),
        (61, 60),
        (60, 61),
        (61, 61),
    )
    day_length = 10

    def __init__(self):
        pygame.mixer.music.load(assets.ost_path("SquareWars"))
        pygame.mixer.music.play()
        self.caption_string = ""
        self.ui_manager = ui.UIManager()
        self.sprites = pygame.sprite.Group()
        self.sprites.add(Cloud(position=(0, 8)))
        self.sprites.add(Cloud(position=(48, -3)))
        self.smoke_timer = timer.Timer(0.1)
        self.pos_index = 0
        self.ui_manager.add(
            ui.Button(
                position=(16, 20),
                image=assets.images["play_button"],
                callback=lambda: setattr(
                    common, "current_state", transition.Transition(current_state=self, next_state=gameplay.Gameplay())
                ),
            ),
            initial_selected=True,
            selector="play_button",
        ).add(
            ui.Button(
                position=(16, 32),
                image=assets.images["settings_button"],
                callback=lambda: setattr(common, "current_state", SettingsMenu()),
            ),
            selector="settings_button",
        ).add_static(ui.Image(position=(8, 3), image=assets.images["menu_title"]), selector="menu_title")

        self.bg_image = assets.images["menu_bg"].copy()
        self.mmm = self.bg_image.get_at((1, 0))
        self.time = 0

        pygame.mixer.music.load(assets.ost_path("SquareWars"))
        pygame.mixer.music.play(loops=-1)

        self.transition_easers: dict[Any, easings.EasyVec] = {}

    def update(self) -> None:
        self.time += common.dt
        self.sprites.update()
        self.ui_manager.update()
        self.smoke_timer.update()
        if not self.smoke_timer.time_left:
            position = ((7, 37), (61, 51))[self.pos_index]
            if random.randint(0, 2):
                self.pos_index = not self.pos_index
            self.sprites.add(Smoke(position))
            self.smoke_timer = timer.Timer(random.random() * 0.5 + 0.5)

    def draw(self, surface=None) -> None:
        if surface is None:
            surface = common.screen
        # day/night cycle
        x = self.time / 15  # fifteen seconds/day (and /night, /dawn, /dusk)
        lerp_value = pygame.math.clamp((abs((x % 4) - 2) - 1) + (abs(((x - 1) % 4) - 2)) / 2, 0, 1)
        # sky
        surface.fill(self.night_color.lerp(self.day_color, lerp_value))
        common.screen.blit(assets.images["menu_bg"], (0, 0))
        # windows
        window_color = self.night_window_color.lerp(self.day_window_color, lerp_value)
        for coord in self.window_coordinates:
            surface.set_at(coord, window_color)
        self.sprites.draw(surface)

        self.ui_manager.draw(surface)

    def transition_update(self) -> None:
        for easer in self.transition_easers.values():
            easer.update()

        p_button = self.ui_manager["play_button"]
        s_button = self.ui_manager["settings_button"]
        t_image = self.ui_manager["menu_title"]

        # speed = 150
        p_button.position = self.transition_easers[p_button].current_pos
        s_button.position = self.transition_easers[s_button].current_pos

        t_image.alpha -= 700 * common.dt
        t_image.alpha2 -= 300 * common.dt
        # t_image.image.set_alpha(t_image.alpha)

        p_button.image.set_alpha(t_image.alpha2)
        s_button.image.set_alpha(t_image.alpha2)

        speed = 150
        self.ui_manager.selector_arrow.rect.x -= speed * common.dt

        self.sprites.update()
        # self.ui_manager.update()
        self.smoke_timer.update()
        if not self.smoke_timer.time_left:
            position = ((7, 37), (61, 51))[self.pos_index]
            if random.randint(0, 2):
                self.pos_index = not self.pos_index
            self.sprites.add(Smoke(position))
            self.smoke_timer = timer.Timer(random.random() * 0.5 + 0.5)

    def transition_draw(self, dst: pygame.Surface) -> None:
        surf = dst.copy()
        surf.fill(self.mmm)
        surf.blit(self.bg_image, (0, 0))
        self.sprites.draw(surf)
        surf.blit(self.ui_manager["menu_title"].image, self.ui_manager["menu_title"].rect)
        surf.set_alpha(self.ui_manager["menu_title"].alpha)
        dst.blit(surf, (0, 0))
        self.ui_manager.draw_exclude_once("menu_title")
        self.ui_manager.draw(dst)

    def transition_init(self):
        # self.ui_manager = deepcopy(self.ui_manager)

        t_image = self.ui_manager["menu_title"]
        t_image.alpha = 255
        t_image.alpha2 = 255

        # def ease(x):
        #     return (
        #         21.38980 * x**7
        #         - 62.23165 * x**6
        #         + 64.67897 * x**5
        #         - 23.29794 * x**4
        #         - 6.39182 * x**3
        #         + 8.21920 * x**2
        #         - 1.37910 * x**1
        #         + 0.00776 * x**0
        #     )

        # RIP, Jiffy no like the actual transition (and I must agree :sob:)
        # def ease(x):
        #     return (
        #         -489051275.67954 * x**25
        #         + 3370247136.69583 * x**24
        #         - 9087988458.11210 * x**23
        #         + 10568251835.33066 * x**22
        #         - 779117597.43718 * x**21
        #         - 9298948490.07450 * x**20
        #         + 3105708851.85429 * x**19
        #         + 8759065407.20914 * x**18
        #         - 4000187023.25428 * x**17
        #         - 8703846651.73520 * x**16
        #         + 5562523752.04632 * x**15
        #         + 8014163229.22339 * x**14
        #         - 9278031238.17117 * x**13
        #         - 3356176679.08941 * x**12
        #         + 13484070599.21112 * x**11
        #         - 13133199227.21771 * x**10
        #         + 7474819587.38848 * x**9
        #         - 2837586721.03713 * x**8
        #         + 745544227.51096 * x**7
        #         - 135737438.22430 * x**6
        #         + 16753941.64108 * x**5
        #         - 1340627.94398 * x**4
        #         + 64480.39264 * x**3
        #         - 1636.02374 * x**2
        #         + 16.50986 * x**1
        #         - 0.01325 * x**0
        #     )

        def ease(x):
            return -1.40837 * x**5 + 3.91918 * x**4 - 3.66444 * x**3 + 2.89393 * x**2 - 0.80336 * x**1 - 0.01371 * x**0

        dist = 50
        time_s = 1

        p_button = self.ui_manager["play_button"]
        self.transition_easers[p_button] = easings.EasyVec(
            ease, p_button.position, pygame.Vector2(p_button.position.x - dist, p_button.position.y), time_s
        )
        s_button = self.ui_manager["settings_button"]
        self.transition_easers[s_button] = easings.EasyVec(
            ease, s_button.position, pygame.Vector2(s_button.position.x + dist, s_button.position.y), time_s
        )


class SettingsMenu:
    caption_string = "Settings"

    def __init__(self):
        super().__init__()
        self.ui_manager = ui.UIManager(without_selector=True)

        slider_rect = pygame.Rect(0, 0, 50, 6)
        slider_rect.center = (settings.LOGICAL_WIDTH / 2, 22)
        self.ui_manager.add(
            ui.Label(
                (settings.LOGICAL_WIDTH / 2, 3),
                "- Settings -",
                font=assets.fonts["silkscreen"],
                bg=(0, 0, 0, 0),
            )
        ).add(
            ui.Label(
                (settings.LOGICAL_WIDTH / 2, 14),
                "Music",
                font=assets.fonts["silkscreen"],
                bg=(0, 0, 0, 0),
            )
        ).add(
            ui.HorizontalSlider(
                slider_rect.copy(),
                initial_value=int(common.music_volume * 100),
                callback=lambda value: setattr(common, "music_volume", value / 100),
            )
        ).add(
            ui.Label(
                (settings.LOGICAL_WIDTH / 2, 29),
                "SFX",
                font=assets.fonts["silkscreen"],
                bg=(0, 0, 0, 0),
            )
        ).add(
            ui.HorizontalSlider(
                slider_rect.move_to(center=(settings.LOGICAL_WIDTH / 2, 37)),
                initial_value=int(common.sfx_volume * 100),
                callback=lambda value: [setattr(common, "sfx_volume", value / 100), assets.sfx["select"].play()],
                do_initial_callback=False,
            )
        )

        if not settings.PYGBAG:
            self.ui_manager.add(
            ui.Button(
                (settings.LOGICAL_WIDTH / 2, 47),
                assets.images["fullscreen_button"],
                e="center",
                callback=self.toggle_fullscreen,
            )
        ).add(
            ui.Button(
                (settings.LOGICAL_WIDTH / 2, 58),
                assets.images["back_button"],
                e="center",
                callback=lambda: setattr(common, "current_state", MainMenu()),
            )
        )
        else:
            self.ui_manager.add(
            ui.Button(
                (settings.LOGICAL_WIDTH / 2, 47),
                assets.images["back_button"],
                e="center",
                callback=lambda: setattr(common, "current_state", MainMenu()),
            )
        )

        # self.particle_manager = particles.ParticleManager(assets.images["particles"])

    def update(self):
        self.ui_manager.update()
        # self.particle_manager.update()

    def draw(self):
        # for pos in [
        #     (0, 0),
        #     (settings.LOGICAL_WIDTH, 0),
        #     (settings.LOGICAL_WIDTH, settings.LOGICAL_HEIGHT),
        #     (0, settings.LOGICAL_HEIGHT),
        # ]:
        #     for _ in range(1):
        #         self.particle_manager.spawn(
        #             pos,
        #             pygame.Vector2(1, 0).rotate(random.randint(0, 359)) * 80,
        #         )
        # self.particle_manager.render(static=True)

        common.screen.fill(pygame.color.Color("#0098dc"))
        common.screen.blit(assets.images["menu_bg"], (0, 0))

        self.ui_manager.draw(common.screen)
        for widget in self.ui_manager.widgets:
            if isinstance(widget, ui.HorizontalSlider):
                widget.draw(common.screen)

    @staticmethod
    def toggle_fullscreen():
        if settings.PYGBAG:
            return
        common.window.destroy()
        if settings.FULLSCREEN:
            common.screen = pygame.display.set_mode(
                (settings.LOGICAL_WIDTH, settings.LOGICAL_HEIGHT), flags=settings.DISPLAY_FLAGS | pygame.HIDDEN
            )
            settings.FULLSCREEN = False
        else:
            common.screen = pygame.display.set_mode(
                (settings.LOGICAL_WIDTH, settings.LOGICAL_HEIGHT),
                flags=settings.DISPLAY_FLAGS | pygame.FULLSCREEN | pygame.HIDDEN,
            )
            settings.FULLSCREEN = True

        window = pygame.Window.from_display_module()
        window.show()
        common.window = window

        if any(settings.DISPLAY_FLAGS & flag for flag in [pygame.SCALED, pygame.OPENGL, pygame.DOUBLEBUF]):
            renderer = pg_sdl2.Renderer.from_window(common.window)
        else:
            renderer = pg_sdl2.Renderer(common.window)
        renderer.draw_color = "#391f21"
