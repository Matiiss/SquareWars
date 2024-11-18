import queue
import collections
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


class Controller:
    def __init__(self):
        self.sprite = None
        self.command_queue = queue.Queue()

    def register_sprite(self, sprite):
        self.sprite = sprite

    def update(self):
        pass


class InputController(Controller):
    def __init__(
        self,
        up_key=pygame.K_w,
        down_key=pygame.K_s,
        left_key=pygame.K_a,
        right_key=pygame.K_d,
        shoot_key=pygame.K_RSHIFT,
    ):
        super().__init__()
        self.up_key = up_key
        self.down_key = down_key
        self.left_key = left_key
        self.right_key = right_key
        self.shoot_key = shoot_key

    def register_sprite(self, sprite):
        self.sprite = sprite

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


class DumbAIController(Controller):
    def __init__(self):
        super().__init__()
        self.team = None
        self.pathfind_queue = queue.Queue()
        self.initial_frame = True

    def register_sprite(self, sprite):
        super().register_sprite(sprite)
        self.team = sprite.team

    def pathfind(self):
        # find nearest target square using BFS
        x, y = int(self.sprite.rect.x / 8), int(self.sprite.rect.y / 8)
        frontier = queue.Queue()
        frontier.put((x, y))
        came_from = {(x, y): None}
        grid = common.current_state.squares
        target_position = None

        while target_position is None:
            if frontier.empty():
                break
            current = frontier.get()
            for next in grid.get_neighbors(current):
                if next not in came_from:
                    frontier.put(next)
                    came_from[next] = current
                    if grid.get_sprite_by_coordinate(*next).team != self.team:
                        target_position = next
        if target_position is None:
            return False
        # contruct path of coordinates to that square
        path = []
        current = target_position
        while current != (x, y):
            path.append(current)
            current = came_from[current]
        path.reverse()
        # convert path of coordinates to commands
        current = (x, y)
        directions = {(0, -1): COMMAND_UP, (0, 1): COMMAND_DOWN, (-1, 0): COMMAND_LEFT, (1, 0): COMMAND_RIGHT}
        stops = {
            COMMAND_UP: COMMAND_STOP_UP,
            COMMAND_DOWN: COMMAND_STOP_DOWN,
            COMMAND_LEFT: COMMAND_STOP_LEFT,
            COMMAND_RIGHT: COMMAND_STOP_RIGHT,
        }
        print((x, y), path)
        for coord in path:
            direction = directions[coord[0] - current[0], coord[1] - current[1]]
            self.pathfind_queue.put(direction)
            self.pathfind_queue.put(stops[direction])
            current = coord
        return True

    def update(self):
        if self.initial_frame:
            self.pathfind()
            self.command_queue.put(Command(self.pathfind_queue.get()))
            self.initial_frame = False
        if self.sprite.half_aligned and self.pathfind_queue.qsize():
            self.command_queue.put(Command(self.pathfind_queue.get()))
            if self.pathfind_queue.qsize():
                self.command_queue.put(Command(self.pathfind_queue.get()))
        if self.pathfind_queue.empty() and self.sprite.aligned:
            if self.pathfind():
                self.command_queue.put(Command(self.pathfind_queue.get()))
