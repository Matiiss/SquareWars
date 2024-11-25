import queue
import pygame
import random

from . import common
from . import settings

COMMAND_UP: int = 0
COMMAND_STOP_UP: int = 1
COMMAND_DOWN: int = 2
COMMAND_STOP_DOWN: int = 3
COMMAND_LEFT: int = 4
COMMAND_STOP_LEFT: int = 5
COMMAND_RIGHT: int = 6
COMMAND_STOP_RIGHT: int = 7
COMMAND_SHOOT: int = 8


class Command:
    def __init__(self, command_name: int):
        self.command_name = command_name


class Controller:
    def __init__(self):
        self.sprite = None
        self.command_queue: queue.Queue[Command] = queue.Queue()

    def register_sprite(self, sprite: pygame.sprite.Sprite) -> None:
        self.sprite = sprite

    def on_motion_input(self) -> None:
        pass

    def update(self) -> None:
        pass


class InputControllerA(Controller):
    def __init__(
        self,
        up_key=pygame.K_w,
        down_key=pygame.K_s,
        left_key=pygame.K_a,
        right_key=pygame.K_d,
        shoot_key=pygame.K_q,
    ):
        super().__init__()
        self.up_key = up_key
        self.down_key = down_key
        self.left_key = left_key
        self.right_key = right_key
        self.shoot_key = shoot_key

    def register_sprite(self, sprite: pygame.sprite.Sprite) -> None:
        self.sprite = sprite

    def on_motion_input(self) -> None:
        keys = pygame.key.get_pressed()
        self.command_queue.put((Command(COMMAND_STOP_UP)))
        self.command_queue.put((Command(COMMAND_STOP_DOWN)))
        self.command_queue.put((Command(COMMAND_STOP_LEFT)))
        self.command_queue.put((Command(COMMAND_STOP_RIGHT)))
        if keys[self.up_key]:
            self.command_queue.put(Command(COMMAND_UP))
        if keys[self.down_key]:
            self.command_queue.put(Command(COMMAND_DOWN))
        if keys[self.left_key]:
            self.command_queue.put(Command(COMMAND_LEFT))
        if keys[self.right_key]:
            self.command_queue.put(Command(COMMAND_RIGHT))

    def update(self) -> None:
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


class InputControllerB(InputControllerA):
    def __init__(
        self,
        up_key=pygame.K_i,
        down_key=pygame.K_k,
        left_key=pygame.K_j,
        right_key=pygame.K_l,
        shoot_key=pygame.K_u,
    ):
        super().__init__(up_key, down_key, left_key, right_key, shoot_key)


class DumbAIController(Controller):
    def __init__(self, dumbness=8):
        super().__init__()
        self.random_latency = dumbness  # increasing this slows the AI down
        self.pathfind_queue = queue.Queue()
        self.initial_frame = True
        self.target_teams = {settings.TEAM_1, settings.TEAM_2, settings.TEAM_NONE}

    def register_sprite(self, sprite: pygame.sprite.Sprite) -> None:
        super().register_sprite(sprite)
        self.target_teams.remove(self.sprite.team)

    def on_motion_input(self):
        self.pathfind_queue = queue.Queue()

    def pathfind(self) -> bool:
        # find nearest target square using BFS
        x, y = int(self.sprite.rect.x / 8), int(self.sprite.rect.y / 8)
        frontier = queue.Queue()
        frontier.put((x, y))
        came_from = {(x, y): None}
        grid = common.current_state.squares
        players = common.current_state.players
        target_position = None

        while target_position is None:
            if frontier.empty():
                break
            current = frontier.get()
            for next in grid.get_neighbors(current):
                if next not in came_from:
                    frontier.put(next)
                    came_from[next] = current
                    square = grid.get_sprite_by_coordinate(*next)
                    if square.team in self.target_teams:
                        for player in players.sprites():
                            if player is self:
                                continue
                            if square.rect.collidepoint(player.rect.center):
                                break
                        else:
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
        for coord in path:
            direction = directions[coord[0] - current[0], coord[1] - current[1]]
            self.pathfind_queue.put(direction)
            self.pathfind_queue.put(stops[direction])
            current = coord
        return True

    def update(self) -> None:
        if self.sprite.powerup is not None:
            self.command_queue.put(Command(COMMAND_SHOOT))
        if (
            self.sprite.aligned
            and common.current_state.squares.get_sprite_by_coordinate(
                int(self.sprite.rect.x / 8), int(self.sprite.rect.y / 8)
            ).team
            in self.target_teams
        ):
            return
        if self.initial_frame:
            self.pathfind()
            self.command_queue.put(Command(self.pathfind_queue.get()))
            self.initial_frame = False
        if self.sprite.half_aligned and self.pathfind_queue.qsize():
            self.command_queue.put(Command(self.pathfind_queue.get()))
        if (
            self.sprite.aligned
            and not self.sprite.speeding_up
            and not random.randint(0, self.random_latency)
        ):
            go = True
            if not self.pathfind_queue.qsize():
                go = self.pathfind()
            if go:
                self.command_queue.put(Command(self.pathfind_queue.get()))
