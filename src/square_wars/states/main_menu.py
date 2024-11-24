from copy import deepcopy

import pygame, random, math

from .. import common, assets, ui, event_types, animation, timer

from .transition import Transition
from .gameplay import Gameplay


class Cloud(pygame.sprite.Sprite):
    SPEED = 8
    def __init__(self, position):
        super().__init__()
        self.image = random.choice(animation.get_spritesheet(assets.images["clouds"], (24, 16)))
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
        self.rect.x = math.sin(self.age * 2) * 3+ self.x

        if self.rect.bottom < 0:
            self.kill()



class MainMenu:
    caption_string = "Main Menu"

    def __init__(self):
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
                    common, "current_state", Transition(current_state=self, next_state=Gameplay())
                ),
            ),
            initial_selected=True,
            selector="play_button",
        ).add(
            ui.Button(position=(16, 32), image=assets.images["settings_button"]), selector="settings_button"
        ).add_static(ui.Image(position=(8, 3), image=assets.images["menu_title"]), selector="menu_title")

    def update(self) -> None:
        self.sprites.update()
        self.ui_manager.update()
        self.smoke_timer.update()
        if not self.smoke_timer.time_left:
            position = (
            (7, 37),
            (61, 51)
            )[self.pos_index]
            if random.randint(0, 2):
                self.pos_index = not self.pos_index
            self.sprites.add(Smoke(position))
            self.smoke_timer = timer.Timer(random.random() * 0.5 + 0.5)

    def draw(self, surface=None) -> None:
        if surface is None:
            surface = common.screen
        surface.blit(assets.images["menu_bg"], (0, 0))
        self.sprites.draw(surface)
        self.ui_manager.draw(surface)

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
        surf.fill("#0098dc")
        surf.set_alpha(self.ui_manager["menu_title"].alpha)
        dst.blit(surf)
        self.ui_manager.draw(dst)

    def transition_init(self):
        # self.ui_manager = deepcopy(self.ui_manager)

        t_image = self.ui_manager["menu_title"]
        t_image.alpha = 255
