from typing import Protocol


class State(Protocol):
    def update(self) -> None: ...

    def draw(self) -> None: ...
