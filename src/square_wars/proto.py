from typing import Protocol

import pygame


class State(Protocol):
    caption_string: str

    def update(self) -> None: ...

    def draw(self) -> None: ...

    def transition_init(self) -> None: ...

    def transition_update(self) -> None: ...

    def transition_draw(self, dst: pygame.Surface) -> None: ...
