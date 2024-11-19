import queue
import random
import pygame
from typing import Iterator

from .. import settings
from .. import command
from .. import common
from .. import animation
from .. import assets
from .. import timer


def center_point_collide(sprite1, sprite2):
    return sprite1.rect.collidepoint(sprite2.rect.center)


class Player(pygame.sprite.Sprite):
    SPEED = 32
    SPEEDY_SPEED = 64

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
        self.speedup_timer = timer.Timer(1)
        self.speedup_timer.end()
        self.blink_timer = timer.Timer(0.1)
        self.blink_on = False
        color = {settings.TEAM_2: "2", settings.TEAM_1: "1"}[self.team]
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

        self.blank_image = pygame.Surface((0, 0))

    @property
    def image(self):
        if self.speedup_timer.time_left and self.blink_on:
            return self.blank_image
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

    def speedup(self, direction):
        self.speedup_timer.restart()
        starts = {
            (0, -1): command.COMMAND_UP,
            (0, 1): command.COMMAND_DOWN,
            (-1, 0): command.COMMAND_LEFT,
            (1, 0): command.COMMAND_RIGHT,
        }
        stops = {
            (0, -1): command.COMMAND_STOP_UP,
            (0, 1): command.COMMAND_STOP_DOWN,
            (-1, 0): command.COMMAND_STOP_LEFT,
            (1, 0): command.COMMAND_STOP_RIGHT,
        }
        stops.pop(direction)
        stops[direction] = starts[direction]
        for value in stops.values():
            self.command_queue.put(command.Command(value))
        self.controller.on_motion_input()

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
                    case command.Command(command_name=command.COMMAND_STOP_UP) if self.moving[1] < 0:
                        self.moving[1] += 1

                    case command.Command(command_name=command.COMMAND_DOWN):
                        self.moving[1] += 1
                    case command.Command(command_name=command.COMMAND_STOP_DOWN) if self.moving[1] > 0:
                        self.moving[1] -= 1

                    case command.Command(command_name=command.COMMAND_LEFT):
                        self.moving[0] -= 1
                    case command.Command(command_name=command.COMMAND_STOP_LEFT) if self.moving[0] < 0:
                        self.moving[0] += 1

                    case command.Command(command_name=command.COMMAND_RIGHT):
                        self.moving[0] += 1
                    case command.Command(command_name=command.COMMAND_STOP_RIGHT) if self.moving[0] > 0:
                        self.moving[0] -= 1

            # prevent motion that runs into something bad
            x, y = int(self.rect.x / 8), int(self.rect.y / 8)
            neighbors = list(common.current_state.squares.get_neighbors((x, y), True))
            if (x + self.moving[0], y + self.moving[1]) not in neighbors:
                if (x + self.moving[0], y) not in neighbors:
                    self.moving[0] = 0
                if (x, y + self.moving[1]) not in neighbors:
                    self.moving[1] = 0
                if (x + self.moving[0], y + self.moving[1]) not in neighbors:
                    self.moving = [0, 0]
                self.controller.on_motion_input()
        speed = self.SPEED
        self.speedup_timer.update()
        if self.speedup_timer.time_left:
            speed = self.SPEEDY_SPEED
        # state handling for visuals
        for anim in self.anim_dict.values():
            anim.update()
        if self.moving != last_moving and pygame.Vector2(last_moving):
            self.last_moving = last_moving
        # actual motion
        if pygame.Vector2(self.moving):
            self.velocity = pygame.Vector2(self.moving)
            self.velocity.scale_to_length(speed)
        else:
            self.velocity = pygame.Vector2()
        self.rect.center += self.velocity * common.dt
        self.rect.clamp_ip((0, 0, 64, 64))
        self.blink_timer.update()
        if not self.blink_timer.time_left:
            self.blink_timer.restart()
            self.blink_on = not self.blink_on


class Speedup(pygame.sprite.Sprite):
    def __init__(self, pos: tuple[int, int]):
        super().__init__()
        self.rect = pygame.FRect(pos, (8, 8))
        x, y = int(pos[0] / 8), int(pos[1] / 8)
        anim_dict = {
            (x, y - 1): ((0, -1), animation.Animation(animation.get_spritesheet(assets.images["speedup"])[2:])),
            (x, y + 1): (
                (0, 1),
                animation.Animation(animation.get_spritesheet(assets.images["speedup"])[2:], flip_y=True),
            ),
            (x - 1, y): (
                (-1, 0),
                animation.Animation(animation.get_spritesheet(assets.images["speedup"])[:2], flip_x=True),
            ),
            (x + 1, y): ((0, 1), animation.Animation(animation.get_spritesheet(assets.images["speedup"])[:2])),
        }
        squares = common.current_state.squares
        for position, (direction, anim) in anim_dict.items():
            if squares.has_at_position(*position) and squares.get_sprite_by_coordinate(*position).team in {
                settings.TEAM_1,
                settings.TEAM_2,
                settings.TEAM_NONE,
            }:
                self.anim = anim
                self.direction = direction
                break
        else:
            self.direction, self.anim = tuple(anim_dict.values())[0]
        self.image = self.anim.image

    def update(self):
        self.anim.update()
        self.image = self.anim.image
        for player in common.current_state.players:
            if self.rect.collidepoint(player.rect.center) and player.aligned:
                player.speedup(self.direction)
                self.kill()


class Square(pygame.sprite.Sprite):
    def __init__(
        self,
        pos: tuple[int, int],
        player_group: pygame.sprite.Group,
        blank_group: pygame.sprite.Group,
        team1_group: pygame.sprite.Group,
        team2_group: pygame.sprite.Group,
        start_team: settings.TEAM_NONE,
    ):
        super().__init__()
        self.rect = pygame.FRect(0, 0, 8, 8)
        self.rect.topleft = pos
        self.player_group = player_group
        self.team_groups = {
            settings.TEAM_NONE: blank_group,
            settings.TEAM_1: team1_group,
            settings.TEAM_2: team2_group,
        }
        self.team = start_team
        self.team_group = None
        if self.team in self.team_groups.keys():
            self.team_group = self.team_groups[self.team]
            self.team_group.add(self)
        self.owner = None
        self.images = dict(
            zip(
                (
                    settings.TEAM_ROCK,
                    settings.TEAM_NONE,
                    settings.TEAM_1,
                    settings.TEAM_2,
                    settings.TEAM_2_SPAWN,
                    settings.TEAM_1_SPAWN,
                ),
                animation.get_spritesheet(assets.images["tileset"]),
            )
        )
        self.occupant = None
        self.teamchange_timer = timer.Timer(0.3)
        self._x = 0
        self._y = 0

    def update(self) -> None:
        self.teamchange_timer.update()
        # check if I collide with any players and change color to match
        changed = False
        if self.team not in {settings.TEAM_ROCK, settings.TEAM_1_SPAWN, settings.TEAM_2_SPAWN}:
            if self.occupant is not None:
                if not self.rect.collidepoint(self.occupant.rect.center):
                    self.occupant = None
                    self.teamchange_timer.restart()
                elif not self.teamchange_timer.time_left and self.owner is not self.occupant:
                    self.team = self.occupant.team
                    self.owner = self.occupant
                    self.owner.squares.add(self)
                    changed = True
            else:
                for sprite in pygame.sprite.spritecollide(self, self.player_group, False, center_point_collide):
                    if sprite is not self.occupant:
                        self.occupant = sprite
                        self.teamchange_timer.restart()
                        if self.occupant.speedup_timer.time_left:
                            self.teamchange_timer.end()
            if changed:
                # update team groups to reflect new ownership
                self.team_group.remove(self)
                self.team_group = self.team_groups[self.team]
                self.team_group.add(self)
                self.owner.squares.remove(self)
        # change color
        self.image = self.images[self.team]


class SquareSpriteGroup(pygame.sprite.Group):
    def __init__(self):
        super().__init__()
        self.grid = {}

    def add_to_grid(self, sprite: Square, x: int, y: int) -> None:
        if sprite.team != settings.TEAM_ROCK:
            self.grid[(x, y)] = sprite
            sprite._x = x
            sprite._y = y
        self.add(sprite)

    def get_neighbors(self, sprite: Square, eight=False) -> Iterator[tuple[int, int]]:
        if eight:
            distances = {1, 2}
        else:
            distances = {1}
        if isinstance(sprite, tuple):
            x, y = sprite
        else:
            x, y = sprite._x, sprite._y
        for nx in range(x - 1, x + 2):
            for ny in range(y - 1, y + 2):
                if abs(nx - x) + abs(ny - y) in distances and (nx, ny) in self.grid.keys():
                    yield nx, ny

    def get_sprite_by_coordinate(self, x: int, y: int) -> Square:
        return self.grid[(x, y)]

    def has_at_position(self, x, y):
        return (x, y) in self.grid


class Gameplay:
    POWERUPS = (Speedup,)

    def __init__(self):
        # timer
        self.timer = timer.Timer(64)
        self.powerup_timer = timer.Timer(2)
        self.caption_string = "TIME: 64"
        # sprite groups
        self.sprites = pygame.sprite.Group()
        self.players = pygame.sprite.Group()
        # handles squares as a graph of neighbouring sprites for BFS
        self.squares = SquareSpriteGroup()
        self.blanks = pygame.sprite.Group()
        self.team_one_squares = pygame.sprite.Group()
        self.team_two_squares = pygame.sprite.Group()
        # decide on rock placement
        rocks = set()
        no_rock_spots = {(0, 0), (7, 7)}
        for _ in range(6):
            nx, ny = random.randint(0, 7), random.randint(0, 7)
            if (nx, ny) in no_rock_spots:
                continue
            rocks.add((nx, ny))
            no_rock_spots.add((nx, ny))
        # spawn grid
        for x in range(0, 8):
            for y in range(0, 8):
                team = settings.TEAM_NONE
                if (x, y) == (0, 0):
                    team = settings.TEAM_1_SPAWN
                if (x, y) == (7, 7):
                    team = settings.TEAM_2_SPAWN
                if (x, y) in rocks:
                    team = settings.TEAM_ROCK
                sprite = Square(
                    (x * 8, y * 8), self.players, self.blanks, self.team_one_squares, self.team_two_squares, team
                )
                self.sprites.add(sprite)
                self.squares.add_to_grid(sprite, x, y)
        # spawn bot player
        controller = command.DumbAIController()
        player = Player(controller, (64 - 8, 64 - 8), settings.TEAM_1)
        self.sprites.add(player)
        self.players.add(player)
        # spawn human player
        controller = command.InputController()
        player = Player(controller, (0, 0), settings.TEAM_2)
        self.sprites.add(player)
        self.players.add(player)
        # play ost
        pygame.mixer.music.load(assets.ost_path("SquareWarsBattle"))
        pygame.mixer.music.play()

    def update(self) -> None:
        self.sprites.update()
        self.caption_string = f"TIME: {int(self.timer.update()):02d}"
        self.powerup_timer.update()
        if not self.powerup_timer.time_left:
            self.powerup_timer.restart()
            while True:
                spot = (random.randint(0, 7), random.randint(0, 7))
                if self.squares.has_at_position(*spot) and self.squares.get_sprite_by_coordinate(*spot).team in {
                    settings.TEAM_1,
                    settings.TEAM_2,
                    settings.TEAM_NONE,
                }:
                    break
            self.sprites.add(random.choice(self.POWERUPS)((spot[0] * 8, spot[1] * 8)))
        if not self.timer.time_left:
            pass

    def draw(self) -> None:
        self.sprites.draw(common.screen)
