from typing import Protocol, runtime_checkable

import pygame

from . import common, assets


class UIManager:
    def __init__(self, without_selector=False):
        self.widgets: list[Widget] = []
        self.static: list[Static] = []
        self.selectables: dict[str, Static | Widget] = {}
        self.without_selector = without_selector
        self.selector_arrow = SelectorArrow()
        self._draw_excludes_once = set()

    def add(self, widget, initial_selected=False, selector: str | None = None):
        if isinstance(widget, Button):
            widget.without_thingy = self.without_selector
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

        if self.without_selector:
            selected = None

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
            if isinstance(widget, HorizontalSlider):
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


class Label(Widget):
    config = {
        "fg": "#ffece3",
        "bg": "#cc6063",
        "hover_fg": "",
        "hover_bg": "",
        "click_fg": "",
        "click_bg": "",
        "width": None,
        "height": None,
        "wraplength": None,
        "font": None,  # welp
        "padx": 0,
        "pady": 0,
        "border_width": 2,
        "border_radius": 0,
    }

    def __init__(self, pos, text, e="center", config: dict | None = None, **kwargs):
        config = type(self).config | kwargs if config is None else type(self).config | config | kwargs
        for key, value in config.items():
            setattr(self, key, value)

        self.font = self.font or assets.fonts["silkscreen"]

        prev_alignment = self.font.align
        self.font.align = pygame.FONT_CENTER
        text_surf = self.font.render(text, False, self.fg)
        self.font.align = prev_alignment

        self.width = self.width or text_surf.get_width() + self.padx * 2
        self.height = self.height or text_surf.get_height() + self.pady * 2

        self.image = pygame.Surface((self.width, self.height), flags=pygame.SRCALPHA)
        self.size_rect = self.image.get_rect()
        self.rect = self.image.get_rect(**{e: pos})

        pygame.draw.rect(self.image, self.bg, self.size_rect, border_radius=self.border_radius)
        self.image.blit(text_surf, text_surf.get_rect(center=self.size_rect.center))

    def update(self):
        pass


class Button:
    def __init__(
        self,
        position,
        image: pygame.Surface,
        e="topleft",
        without_thingy=False,
        callback=lambda: None,
    ) -> None:
        self.position = pygame.Vector2(position)
        self.image = image.copy()
        self.callback = callback
        self.is_hovered = False
        self.is_pressed = False
        self.e = e
        self.without_thingy = without_thingy

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

        if self.is_hovered and not self.without_thingy:
            position.x += 2
            # rect.width += 1

        setattr(rect, self.e, position)
        return rect

    @property
    def collide_rect(self) -> pygame.Rect:
        rect = self.image.get_rect()
        position = self.position.copy()

        if self.is_hovered and not self.without_thingy:
            rect.width += 2

        setattr(rect, self.e, position)
        return rect


class HorizontalSlider(Widget):
    def __init__(
        self,
        rect: pygame.Rect,
        min_value: int = 0,
        max_value: int = 100,
        step: int = 1,
        callback: callable = lambda _: None,
        initial_value: int = 50,
    ):
        self.min_value = min_value
        self.max_value = max_value
        self.range = max_value - min_value
        self.step = min(self.range, max(step, self.range // rect.width))
        self.callback = callback
        self.rail = rect.inflate(0, -0.8 * rect.height)
        self.x, self.y = rect.center
        self.radius = int(rect.width * 0.05)
        self.clicked = False
        self.prev_value = 0

        self.value = initial_value

    def update(self) -> None:
        for event in common.events:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.collision(event.pos):
                self.clicked = True
            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1 and self.clicked:
                self.clicked = False
                value = self.value
                if self.prev_value != value:
                    self.prev_value = value

            elif event.type == pygame.MOUSEMOTION and self.clicked:
                self.x, self.y = self.clamp_rail(event.pos)
                self.value = round(self.value / self.step) * self.step

    def collision(self, pos: tuple[int, int]) -> bool:
        mx, my = pos
        dx, dy = abs(self.x - mx), abs(self.y - my)
        if dx**2 + dy**2 <= self.radius**2:
            return True
        return False

    def draw(self, surface: pygame.Surface) -> None:
        pygame.draw.rect(surface, "#cc6063", self.rail)
        pygame.draw.circle(surface, "#ffece3", (self.x, self.y), self.radius)

    def clamp_rail(self, pos: tuple[int, int]) -> tuple[int, int]:
        x, y = pos
        new_x = max(self.rail.left + self.radius, min(x, self.rail.right - self.radius))
        return new_x, self.rail.centery

    @property
    def value(self) -> int:
        distance = self.x - (self.rail.left + self.radius)
        rel_val = distance / (self.rail.width - 2 * self.radius)
        value = self.min_value + round((self.range * rel_val) / self.step) * self.step
        return value

    @value.setter
    def value(self, value: int) -> None:
        value = value and round(value / self.step) * self.step - self.min_value
        rel_val = value / self.range
        new_rel_pos = round(rel_val * (self.rail.width - 2 * self.radius))
        self.x = new_rel_pos + self.rail.left + self.radius
        value += self.min_value
        self.prev_value = value
        self.callback(value)
