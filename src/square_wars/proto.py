from typing import Protocol


class State(Protocol):
    caption_string: str

    def update(self) -> None: ...

    def draw(self) -> None: ...
