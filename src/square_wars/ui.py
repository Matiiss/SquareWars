from typing import Protocol

import pygame

from . import common, assets


class UIManager:
    def __init__(self):
        self.widgets: list[Widget] = []
        self.selector_arrow = SelectorArrow()

    def add(self, *widgets, initial_selected=False):
        if not initial_selected:
            self.widgets.extend(widgets)
        elif initial_selected and len(widgets) == 1:
            self.widgets.append(widgets[0])
            self.selector_arrow.last_selection = widgets[0]
            self.selector_arrow.shown = True
            self.selector_arrow.rect.midright = pygame.Vector2(widgets[0].rect.midleft) - (
                self.selector_arrow.dist,
                0,
            )
            self.selector_arrow.current_idx = len(self.widgets) - 1
        else:
            raise Exception("only one initial selected can be specified at a time")
        return self

    def update(self):
        selected = None
        for event in common.events:
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_s, pygame.K_DOWN):
                    self.selector_arrow.current_idx += 1
                    if self.selector_arrow.current_idx >= len(self.widgets):
                        self.selector_arrow.current_idx = len(self.widgets) - 1
                    if self.widgets:
                        selected = self.widgets[self.selector_arrow.current_idx]
                elif event.key in (pygame.K_w, pygame.K_UP):
                    self.selector_arrow.current_idx -= 1
                    if self.selector_arrow.current_idx < 0:
                        self.selector_arrow.current_idx = 0
                    if self.widgets:
                        selected = self.widgets[self.selector_arrow.current_idx]
                elif event.key == pygame.K_RETURN:
                    if self.selector_arrow.last_selection is not None:
                        self.selector_arrow.last_selection.is_pressed = True
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_RETURN:
                    if self.selector_arrow.last_selection is not None:
                        getattr(self.selector_arrow.last_selection, "callback", lambda: None)()

        for widget in self.widgets:
            widget.update()
            if getattr(widget, "is_hovered", False):
                if selected is None:
                    selected = widget
                else:
                    widget.is_hovered = False

        if selected is not None:
            self.selector_arrow.rect.midright = pygame.Vector2(selected.collide_rect.midleft) - (
                self.selector_arrow.dist,
                0,
            )
            self.selector_arrow.shown = True
            self.selector_arrow.last_selection = selected
        elif self.selector_arrow.last_selection is None:
            self.selector_arrow.shown = False

        if self.selector_arrow.last_selection is not None:
            self.selector_arrow.last_selection.is_hovered = True

    def draw(self, dst: pygame.Surface) -> None:
        for widget in self.widgets:
            dst.blit(widget.image, widget.rect)

        if self.selector_arrow.shown:
            dst.blit(self.selector_arrow.image, self.selector_arrow.rect)


class Widget(Protocol):
    image: pygame.Surface
    rect: pygame.Rect | pygame.FRect
    collide_rect: pygame.Rect | pygame.FRect

    def update(self) -> None: ...


class SelectorArrow:
    def __init__(self, dist=2):
        self.dist = dist
        self.image = assets.images["selector_arrow"]
        self.rect = self.image.get_rect()
        self.shown = False
        self.last_selection = None
        self.current_idx = 0


class Button:
    def __init__(
        self,
        position,
        image,
        callback=lambda: None,
    ) -> None:
        self.position = pygame.Vector2(position)
        self.image = image
        self.callback = callback
        self.is_hovered = False
        self.is_pressed = False

    def update(self):
        for event in common.events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                self.is_pressed = event.button == pygame.BUTTON_LEFT and self.collide_rect.collidepoint(event.pos)

            elif event.type == pygame.MOUSEBUTTONUP:
                if self.is_pressed and self.collide_rect.collidepoint(event.pos):
                    self.callback()
                self.is_pressed = False

            elif event.type == pygame.MOUSEMOTION:
                self.is_hovered = self.collide_rect.collidepoint(event.pos)

    @property
    def rect(self) -> pygame.Rect:
        rect = self.image.get_rect()
        position = self.position.copy()

        if self.is_hovered:
            position.x += 1
            # rect.width += 1

        rect.topleft = position
        return rect

    @property
    def collide_rect(self) -> pygame.Rect:
        rect = self.image.get_rect()
        position = self.position.copy()

        if self.is_hovered:
            rect.width += 1

        rect.topleft = position
        return rect
