from copy import deepcopy

import pygame

from .. import common, assets, ui, event_types

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

    def update(self) -> None:
        self.ui_manager.update()

    def draw(self) -> None:
        # common.screen.blit(assets.images["menu_bg"], (0, 0))
        common.screen.fill("darkgreen")
        self.ui_manager.draw(common.screen)

    def transition_update(self) -> None:
        p_button = self.ui_manager["play_button"]
        s_button = self.ui_manager["settings_button"]
        t_image = self.ui_manager["menu_title"]

        speed = 150
        p_button.position.y -= speed * common.dt
        s_button.position.y += speed * common.dt

        t_image.alpha -= 700 * common.dt
        t_image.image.set_alpha(t_image.alpha)

        self.ui_manager.selector_arrow.rect.x -= speed * common.dt

    def transition_draw(self, dst: pygame.Surface) -> None:
        surf = dst.copy()
        surf.fill("darkgreen")
        surf.set_alpha(self.ui_manager["menu_title"].alpha)
        dst.blit(surf)
        self.ui_manager.draw(dst)

    def transition_init(self):
        # self.ui_manager = deepcopy(self.ui_manager)

        t_image = self.ui_manager["menu_title"]
        t_image.alpha = 255
