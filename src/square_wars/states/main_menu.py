import pygame

from .. import common, assets, ui, event_types


class MainMenu:
    caption_string = "Main Menu"

    def __init__(self):
        self.ui_manager = ui.UIManager()
        self.ui_manager.add(
            ui.Button(
                position=(16, 28),
                image=assets.images["play_button"],
                callback=lambda: pygame.event.post(pygame.Event(event_types.SWITCH_TO_GAMEPLAY)),
            ),
            initial_selected=True,
        ).add(ui.Button(position=(16, 39), image=assets.images["settings_button"]))

    def update(self) -> None:
        self.ui_manager.update()

    def draw(self) -> None:
        # common.screen.blit(assets.images["menu_bg"], (0, 0))
        common.screen.fill("darkgreen")
        common.screen.blit(assets.images["menu_title"], (8, 13))
        self.ui_manager.draw(common.screen)
