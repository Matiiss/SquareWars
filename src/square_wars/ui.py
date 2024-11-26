from typing import Protocol, runtime_checkable

import pygame

from . import common, assets


class UIManager:
    def __init__(self):
        self.widgets: list[Widget] = []
        self.static: list[Static] = []
        self.selectables: dict[str, Static | Widget] = {}
        self.selector_arrow = SelectorArrow()
        self._draw_excludes_once = set()

    def add(self, widget, initial_selected=False, selector: str | None = None):
        if not initial_selected:
            self.widgets.append(widget)
        else:
            self.widgets.append(widget)
            self.selector_arrow.last_selection = widget
            self.selector_arrow.shown = True
            self.selector_arrow.rect.midright = pygame.Vector2(widget.rect.midleft) - (
                self.selector_arrow.dist,
                0,
            )
            self.selector_arrow.current_idx = len(self.widgets) - 1

        self._add_selectable(widget=widget, selector=selector)
        if hasattr(widget, "set_ui"):
            widget.set_ui(self)

        return self

    def add_static(self, widget, selector: str | None):
        self.static.append(widget)
        self._add_selectable(widget=widget, selector=selector)
        return self

    def _add_selectable(self, widget, selector: str | None) -> None:
        if selector is None:
            return

        if selector in self.selectables:
            raise ValueError("duplicate selectors not allowed")

        self.selectables[selector] = widget

    def __getitem__(self, item: str) -> "Static | Widget":
        return self.selectables[item]

    def draw_exclude_once(self, selector: str):
        self._draw_excludes_once.add(self.selectables[selector])

    def update(self):
        self._draw_excludes_once.clear()

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
                -1,
            )
            self.selector_arrow.shown = True
            self.selector_arrow.last_selection = selected
        elif self.selector_arrow.last_selection is None:
            self.selector_arrow.shown = False

        if self.selector_arrow.last_selection is not None:
            self.selector_arrow.last_selection.is_hovered = True

    def draw(self, dst: pygame.Surface) -> None:
        for widget in self.widgets:
            if widget in self._draw_excludes_once:
                continue
            dst.blit(widget.image, widget.rect)

        for widget in self.static:
            if widget in self._draw_excludes_once:
                continue
            dst.blit(widget.image, widget.rect)

        if self.selector_arrow.shown:
            dst.blit(self.selector_arrow.image, self.selector_arrow.rect)


@runtime_checkable
class Static(Protocol):
    image: pygame.Surface
    rect: pygame.Rect | pygame.FRect


class Widget(Static):
    position: pygame.Vector2
    collide_rect: pygame.Rect | pygame.FRect

    def update(self) -> None: ...


class SelectorArrow:
    def __init__(self, dist=2):
        self.dist = dist
        self.image = assets.images["selector_arrow"]
        self.rect = self.image.get_frect()
        self.shown = False
        self.last_selection = None
        self.current_idx = 0


class Image:
    def __init__(self, position, image: pygame.Surface) -> None:
        self.image = image.copy()
        self.rect = image.get_rect(topleft=position)


class DayNightBG:

    def __init__(self):
        self.position = pygame.Vector2()
        self.rect = pygame.Rect(0, 0, 64, 64)
        self.image = pygame.Surface((64, 64)).convert()
        self.bg_image = assets.images["menu_bg"]
        self.time = 0
        
    def update(self):
        self.time += common.dt
        # add two 90 degree out-of-phase triangle waves to make a trapezoid
        x = self.time / 5  # five seconds/day (and /night, /dawn, /dusk)
        self.lerp_value = pygame.math.clamp((abs((x % 4) - 2) - 1) + (abs(((x - 1) % 4) - 2)) / 2, 0, 1)
        self.image.fill

class Button:
    def __init__(
        self,
        position,
        image,
        callback=lambda: None,
    ) -> None:
        self.position = pygame.Vector2(position)
        self.image = image.copy()
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
            position.x += 2
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
