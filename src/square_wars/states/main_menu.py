import pygame

from .. import common, assets, ui


class MainMenu:
    caption_string = "Main Menu"

    def __init__(self):
        self.ui_manager = ui.UIManager()
        self.ui_manager.add(ui.Button((16, 28), assets.images["play_button"]), initial_selected=True).add(
            ui.Button((16, 39), assets.images["settings_button"])
        )

    def update(self) -> None:
        self.ui_manager.update()

    def draw(self) -> None:
        # common.screen.blit(assets.images["menu_bg"], (0, 0))
        common.screen.fill("darkgreen")
        common.screen.blit(assets.images["menu_title"], (8, 13))
        self.ui_manager.draw(common.screen)
