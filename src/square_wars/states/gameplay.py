import queue
import pygame
from typing import Iterator

from .. import settings
from .. import command
from .. import common
from .. import animation
from .. import assets


def center_point_collide(sprite1, sprite2):
    return sprite1.rect.collidepoint(sprite2.rect.center)


class Player(pygame.sprite.Sprite):
    SPEED = 8

    def __init__(self, controller: command.Controller, pos: tuple[int, int], team: int):
        super().__init__()
        self.controller = controller
        self.team = team
        self.rect = pygame.FRect(0, 0, 8, 8)
        self.rect.topleft = pos
        self.moving = [0, 0]
        self.last_moving = [0, 1]
        self.command_queue = queue.Queue()
        self.squares = pygame.sprite.Group()
        color = {settings.TEAM_BROWN: "Brown", settings.TEAM_ORANGE: "Orange"}[self.team]
        self.anim_dict = {
            (-1, -1): animation.Animation(animation.get_spritesheet(assets.images[f"Mr{color}Back"]), flip_x=True),
            (0, -1): animation.Animation(animation.get_spritesheet(assets.images[f"Mr{color}Back"]), flip_x=True),
            (1, -1): animation.Animation(animation.get_spritesheet(assets.images[f"Mr{color}Back"])),
            (1, 0): animation.Animation(animation.get_spritesheet(assets.images[f"Mr{color}"])),
            (1, 1): animation.Animation(animation.get_spritesheet(assets.images[f"Mr{color}"])),
            (0, 1): animation.Animation(animation.get_spritesheet(assets.images[f"Mr{color}"])),
            (-1, 1): animation.Animation(animation.get_spritesheet(assets.images[f"Mr{color}"]), flip_x=True),
            (-1, 0): animation.Animation(animation.get_spritesheet(assets.images[f"Mr{color}"]), flip_x=True),
        }

        self.controller.register_sprite(self)

    @property
    def image(self):
        facing = self.moving
        if not pygame.Vector2(self.moving):
            facing = self.last_moving
        if not pygame.Vector2(self.moving):
            self.anim_dict[tuple(facing)].restart()
        return self.anim_dict[tuple(facing)].image

    @property
    def aligned(self):
        return int(self.rect.x) % 8 == 0 and int(self.rect.y) % 8 == 0

    @property
    def half_aligned(self):
        return (int(self.rect.x) % 8, int(self.rect.y) % 8) in {(0, 4), (4, 0), (4, 4)}

    def update(self) -> None:
        # Do command reading in 2 stages
        # Stage 1: realtime, cache non-realtime commands
        self.controller.update()
        while self.controller.command_queue.qsize():
            next_command = self.controller.command_queue.get()
            if next_command.command_name == command.COMMAND_SHOOT:
                print("pew pew")
            else:
                self.command_queue.put(next_command)
        # Stage 2: evaluate motion commands only when player is aligned with the grid
        # Ensures that the player cannot stop motion or change direction when not aligned
        last_moving = list(self.moving)
        if self.aligned:
            while self.command_queue.qsize():
                next_command = self.command_queue.get()
                match next_command:
                    case command.Command(command_name=command.COMMAND_UP):
                        self.moving[1] -= 1
                    case command.Command(command_name=command.COMMAND_STOP_UP):
                        self.moving[1] += 1

                    case command.Command(command_name=command.COMMAND_DOWN):
                        self.moving[1] += 1
                    case command.Command(command_name=command.COMMAND_STOP_DOWN):
                        self.moving[1] -= 1

                    case command.Command(command_name=command.COMMAND_LEFT):
                        self.moving[0] -= 1
                    case command.Command(command_name=command.COMMAND_STOP_LEFT):
                        self.moving[0] += 1

                    case command.Command(command_name=command.COMMAND_RIGHT):
                        self.moving[0] += 1
                    case command.Command(command_name=command.COMMAND_STOP_RIGHT):
                        self.moving[0] -= 1
        # state handling for visuals
        for anim in self.anim_dict.values():
            anim.update()
        if self.moving != last_moving and pygame.Vector2(last_moving):
            self.last_moving = last_moving
            print(self.last_moving)
        # actual motion
        if pygame.Vector2(self.moving):
            self.velocity = pygame.Vector2(self.moving)
            self.velocity.scale_to_length(self.SPEED)
        else:
            self.velocity = pygame.Vector2()
        self.rect.center += self.velocity * common.dt
        self.rect.clamp_ip((0, 0, 64, 64))


class Square(pygame.sprite.Sprite):
    def __init__(
        self,
        pos: tuple[int, int],
        player_group: pygame.sprite.Group,
        blank_group: pygame.sprite.Group,
        orange_group: pygame.sprite.Group,
        brown_group: pygame.sprite.Group,
    ):
        super().__init__()
        self.rect = pygame.FRect(0, 0, 8, 8)
        self.rect.topleft = pos
        self.player_group = player_group
        self.team_groups = {
            settings.TEAM_NONE: blank_group,
            settings.TEAM_ORANGE: orange_group,
            settings.TEAM_BROWN: brown_group,
        }
        self.team = settings.TEAM_NONE
        self.team_group = self.team_groups[self.team]
        self.team_group.add(self)
        self.owner = None
        self.image = pygame.Surface((8, 8)).convert()
        self.image.fill(settings.BLANK_COLOR)
        self._x = 0
        self._y = 0

    def update(self) -> None:
        # check if I collide with any players and change color to match
        changed = False
        for sprite in pygame.sprite.spritecollide(self, self.player_group, False, center_point_collide):
            if sprite is not self.owner:
                self.team = sprite.team
                self.owner = sprite
                self.owner.squares.add(self)
                changed = True
        if changed:
            # update team groups to reflect new ownership
            self.team_group.remove(self)
            self.team_group = self.team_groups[self.team]
            self.team_group.add(self)
            self.owner.squares.remove(self)
            # change color
            if self.team == settings.TEAM_BROWN:
                color = settings.BROWN_COLOR
            if self.team == settings.TEAM_ORANGE:
                color = settings.ORANGE_COLOR
            if self.team == settings.TEAM_NONE:
                color = settings.BLANK_COLOR
            self.image.fill(color)


class SquareSpriteGroup(pygame.sprite.Group):
    def __init__(self):
        super().__init__()
        self.grid = {}

    def add_to_grid(self, sprite: Square, x: int, y: int) -> None:
        self.grid[(x, y)] = sprite
        sprite._x = x
        sprite._y = y
        self.add(sprite)

    def get_neighbors(self, sprite: Square) -> Iterator[tuple[int, int]]:
        if isinstance(sprite, tuple):
            x, y = sprite
        else:
            x, y = sprite._x, sprite._y
        for nx in range(x - 1, x + 2):
            for ny in range(y - 1, y + 2):
                if abs(nx - x) + abs(ny - y) == 1 and (nx, ny) in self.grid.keys():
                    yield nx, ny

    def get_sprite_by_coordinate(self, x: int, y: int) -> Square:
        return self.grid[(x, y)]


class Gameplay:
    def __init__(self):
        # sprite groups
        self.sprites = pygame.sprite.Group()
        self.players = pygame.sprite.Group()
        # handles squares as a graph of neighbouring sprites for BFS
        self.squares = SquareSpriteGroup()
        self.blanks = pygame.sprite.Group()
        self.oranges = pygame.sprite.Group()
        self.browns = pygame.sprite.Group()
        # spawn squares
        for x in range(0, 8):
            for y in range(0, 8):
                sprite = Square((x * 8, y * 8), self.players, self.blanks, self.oranges, self.browns)
                self.sprites.add(sprite)
                self.squares.add_to_grid(sprite, x, y)
        # spawn human player
        controller = command.DumbAIController()
        player = Player(controller, (64 - 8, 64 - 8), settings.TEAM_ORANGE)
        self.sprites.add(player)
        self.players.add(player)
        # spawn bot player
        controller = command.InputController()
        player = Player(controller, (0, 0), settings.TEAM_BROWN)
        self.sprites.add(player)
        self.players.add(player)

    def update(self) -> None:
        self.sprites.update()

    def draw(self) -> None:
        self.sprites.draw(common.screen)
