import queue
import pygame

from . import common
from . import settings

COMMAND_UP = 0
COMMAND_STOP_UP = 1
COMMAND_DOWN = 2
COMMAND_STOP_DOWN = 3
COMMAND_LEFT = 4
COMMAND_STOP_LEFT = 5
COMMAND_RIGHT = 6
COMMAND_STOP_RIGHT = 7
COMMAND_SHOOT = 8

class Command:
    def __init__(self, command_name):
        self.command_name = command_name

class InputController:
    def __init__(self, up_key=pygame.K_w, down_key=pygame.K_s, left_key=pygame.K_a, right_key=pygame.K_d, shoot_key=pygame.K_RSHIFT):
        self.up_key = up_key
        self.down_key = down_key
        self.left_key = left_key
        self.right_key = right_key
        self.shoot_key = shoot_key
        self.command_queue = queue.Queue()

    def update(self):
        for event in common.events:
            if event.type == pygame.KEYDOWN:
                if event.key == self.up_key:
                    self.command_queue.put(Command(COMMAND_UP))
                if event.key == self.down_key:
                    self.command_queue.put(Command(COMMAND_DOWN))
                if event.key == self.left_key:
                    self.command_queue.put(Command(COMMAND_LEFT))
                if event.key == self.right_key:
                    self.command_queue.put(Command(COMMAND_RIGHT))
                if event.key == self.shoot_key:
                    self.command_queue.put(Command(COMMAND_SHOOT))
            if event.type == pygame.KEYUP:
                if event.key == self.up_key:
                    self.command_queue.put(Command(COMMAND_STOP_UP))
                if event.key == self.down_key:
                    self.command_queue.put(Command(COMMAND_STOP_DOWN))
                if event.key == self.left_key:
                    self.command_queue.put(Command(COMMAND_STOP_LEFT))
                if event.key == self.right_key:
                    self.command_queue.put(Command(COMMAND_STOP_RIGHT))