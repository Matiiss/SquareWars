import time
from typing import Any

import pygame

from .. import common, assets, ui, utils, easings

from .transition import Transition
from .gameplay import Gameplay


class MainMenu:
    caption_string = "Main Menu"

    def __init__(self):
        self.ui_manager = ui.UIManager()
        self.ui_manager.add(
            ui.Button(
                position=(16, 28),
                image=assets.images["play_button"],
                callback=lambda: setattr(
                    common, "current_state", Transition(current_state=self, next_state=Gameplay())
                ),
            ),
            initial_selected=True,
            selector="play_button",
        ).add(
            ui.Button(position=(16, 39), image=assets.images["settings_button"]), selector="settings_button"
        ).add_static(ui.Image(position=(8, 13), image=assets.images["menu_title"]), selector="menu_title")

        self.bg_image = utils.nine_slice(utils.get_sprite_sheet(assets.images["guiWoodBG"]), (64, 64))
        self.mmm = self.bg_image.get_at((1, 0))

        pygame.mixer.music.load(assets.ost_path("SquareWars"))
        pygame.mixer.music.play(loops=-1)

        self.transition_easers: dict[Any, Easy] = {}

    def update(self) -> None:
        self.ui_manager.update()

    def draw(self, surface=None) -> None:
        # common.screen.blit(assets.images["menu_bg"], (0, 0))
        if surface is None:
            surface = common.screen

        surface.fill(self.mmm)
        surface.blit(self.bg_image, (0, 0))
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

    def transition_draw(self, dst: pygame.Surface) -> None:
        surf = dst.copy()
        surf.fill(self.mmm)
        surf.blit(self.bg_image, (0, 0))
        surf.blit(self.ui_manager["menu_title"].image, self.ui_manager["menu_title"].rect)
        surf.set_alpha(self.ui_manager["menu_title"].alpha)
        dst.blit(surf)
        self.ui_manager.draw_exclude_once("menu_title")
        self.ui_manager.draw(dst)

    def transition_init(self):
        # self.ui_manager = deepcopy(self.ui_manager)

        t_image = self.ui_manager["menu_title"]
        t_image.alpha = 255
        t_image.alpha2 = 255

        def ease(x):
            return (
                21.38980 * x**7
                - 62.23165 * x**6
                + 64.67897 * x**5
                - 23.29794 * x**4
                - 6.39182 * x**3
                + 8.21920 * x**2
                - 1.37910 * x**1
                + 0.00776 * x**0
            )

        dist = 100
        time_s = 1

        p_button = self.ui_manager["play_button"]
        self.transition_easers[p_button] = Easy(
            ease, p_button.position, pygame.Vector2(p_button.position.x, p_button.position.y - dist), time_s
        )
        s_button = self.ui_manager["settings_button"]
        self.transition_easers[s_button] = Easy(
            ease, s_button.position, pygame.Vector2(s_button.position.x, s_button.position.y + dist), time_s
        )


class Easy:
    def __init__(
        self,
        easing,
        start_pos: pygame.Vector2,
        end_pos: pygame.Vector2,
        total_time_s: float,
        start_immediately: bool = True,
    ) -> None:
        self.easing = easing

        self.start_pos = start_pos.copy()
        self.end_pos = end_pos.copy()
        self.current_pos = self.start_pos.copy()

        self.total_time_s = total_time_s
        self.start_time_s = time.perf_counter()

    def update(self):
        elapsed_time_s = time.perf_counter() - self.start_time_s
        if elapsed_time_s > self.total_time_s:
            self.current_pos = self.end_pos
            return

        time_fraction = elapsed_time_s / self.total_time_s
        print(time_fraction)
        x = easings.scale(self.start_pos.x, self.end_pos.x, self.easing(time_fraction))
        y = easings.scale(self.start_pos.y, self.end_pos.y, self.easing(time_fraction))
        self.current_pos = pygame.Vector2(x, y)
