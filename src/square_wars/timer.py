import pygame

from . import common


class Timer:
    def __init__(self, amount: float):
        self.time_left: float = amount
        self.max_time: float = amount

    def update(self) -> float:
        self.time_left = max(self.time_left - common.dt, 0)
        return self.time_left

    def restart(self):
        self.time_left = self.max_time

    def end(self):
        self.time_left = 0
