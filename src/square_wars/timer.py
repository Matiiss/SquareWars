import pygame

from . import common

class Timer:
    def __init__(self, amount: float):
        self.time_left: float = amount

    def update(self) -> float:
        self.time_left = max(self.time_left - common.dt, 0)
        return self.time_left