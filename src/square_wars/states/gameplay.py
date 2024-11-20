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


class Bullet(pygame.sprite.Sprite):
    SPEED = 64
    def __init__(self, pos: tuple[int, int], direction: pygame.Vector2, owner: pygame.sprite.Sprite):
        super().__init__()
        self.image = pygame.Surface((1, 1))
        self.image.fill("#131313")
        self.rect = pygame.FRect(pos, (1, 1))
        self.velocity = direction.normalize() * self.SPEED
        self.owner = owner

    def update(self):
        self.rect.center += self.velocity * common.dt
        for player in common.current_state.players:
            if player.rect.colliderect(self.rect) and player is not self.owner:
                player.whack()
                self.kill()



class Explosion(pygame.sprite.Sprite):
    def __init__(self, pos: tuple[int, int]):
        super().__init__()
        self.rect = pygame.FRect(pos, (8, 8))
        self.anim = animation.NoLoopAnimation(animation.get_spritesheet(assets.images["explosion"]))
        self.image = self.anim.image

    def update(self):
        self.anim.update()
        self.image = self.anim.image
        x, y = int(self.rect.x / 8), int(self.rect.y / 8)
        common.current_state.squares.get_sprite_by_coordinate(x, y).reset()
        for player in common.current_state.players:
            if self.rect.collidepoint(player.rect.center):
                player.whack()
        if self.anim.done():
            self.kill()


class Player(pygame.sprite.Sprite):
    SPEED = 32
    SPEEDY_SPEED = 64
    GHOST_SPEED = 32

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
        self.align_flag = False
        self.powerup = None
        self.spawn_point = self.rect.topleft
        self.ghost_anim = animation.SingleAnimation(assets.images["ghost"])
        self.whacked = False
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
    def facing(self):
        if not pygame.Vector2(self.moving):
            return self.last_moving
        return self.moving

    @property
    def image(self):
        if self.whacked:
            return self.ghost_anim.image
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
        if int(self.rect.x) % 8 == 0 and int(self.rect.y) % 8 == 0:
            if self.align_flag:
                return False
            return True

    @property
    def half_aligned(self):
        return (int(self.rect.x) % 8, int(self.rect.y) % 8) in {(0, 4), (4, 0), (4, 4)}

    def speedup(self, direction):
        self.speedup_timer.restart()
        self.moving = list(direction)

    def set_powerup(self, sprite):
        if self.powerup is not None:
            self.powerup.kill()
        self.powerup = sprite

    def dequip_powerup(self):
        self.powerup = None

    def whack(self):
        assets.sfx["whack"].play()
        self.whacked = True

    def update(self) -> None:
        if not self.whacked:
            # Do command reading in 2 stages
            # Stage 1: realtime, cache non-realtime commands
            self.controller.update()
            while self.controller.command_queue.qsize():
                next_command = self.controller.command_queue.get()
                if next_command.command_name == command.COMMAND_SHOOT:
                    print("pew pew")
                    if self.powerup:
                        self.powerup.use()
                else:
                    self.command_queue.put(next_command)
            # Stage 2: evaluate motion commands only when player is aligned with the grid
            # Ensures that the player cannot stop motion or change direction when not aligned
            last_moving = list(self.moving)
            if self.aligned and self.speedup_timer.time_left < 0.5:
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
            self.moving[0] = pygame.math.clamp(self.moving[0], -1, 1)
            self.moving[1] = pygame.math.clamp(self.moving[1], -1, 1)
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
            motion = self.velocity * common.dt
            self.rect.x += motion.x
            rect = pygame.Rect(self.rect)
            moved = False
            for sprite in common.current_state.squares:
                if sprite.team == settings.TEAM_ROCK and sprite.rect.colliderect(rect):
                    if motion.x >= 0:
                        self.rect.right = sprite.rect.left
                        moved = True
                    else:
                        self.rect.left = sprite.rect.right
                        moved = True
            self.rect.y += motion.y
            rect = pygame.Rect(self.rect)
            for sprite in common.current_state.squares:
                if sprite.team == settings.TEAM_ROCK and sprite.rect.colliderect(rect):
                    if motion.y >= 0:
                        self.rect.bottom = sprite.rect.top
                        moved = True
                    else:
                        self.rect.top = sprite.rect.bottom
                        moved = True
            if moved:
                self.controller.on_motion_input()
            self.rect.clamp_ip((0, 0, 64, 64))
            self.blink_timer.update()
            if not self.blink_timer.time_left:
                self.blink_timer.restart()
                self.blink_on = not self.blink_on
        else:
            self.ghost_anim.update()
            self.rect.topleft = pygame.Vector2(self.rect.topleft).move_towards(self.spawn_point, self.GHOST_SPEED * common.dt)
            if self.rect.topleft == self.spawn_point:
                self.ghost_anim.restart()
                self.whacked = False


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
            if common.current_state.squares.is_clear_position(*position):
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
                assets.sfx["speedup"].play()
                player.speedup(self.direction)
                self.kill()


class ShotGun(pygame.sprite.Sprite):
    def __init__(self, pos: tuple[int, int]):
        super().__init__()
        self.image = assets.images["gun"]
        self.rect = pygame.Rect(pos, (8, 8))
        self.player = None

    def update(self):
        if self.player is None:
            for player in common.current_state.players:
                if self.rect.collidepoint(player.rect.center) and player.aligned:
                    player.set_powerup(self)
                    self.player = player
                    assets.sfx["pickup"].play()
        else:
            if self.player.rect.top < 8:
                self.rect.center = self.player.rect.midbottom
            else:
                self.rect.center = self.player.rect.midtop

    def use(self):
        assets.sfx["gunshot"].play()
        common.current_state.sprites.add(Bullet(self.rect.center, pygame.Vector2(self.player.facing), self.player))
        self.player.dequip_powerup()
        self.kill()


class GasCan(pygame.sprite.Sprite):
    def __init__(self, pos: tuple[int, int]):
        super().__init__()
        frames = animation.get_spritesheet(assets.images["gascan"])
        self.anim_dict = {
            "idle": animation.SingleAnimation(frames[0]),
            "lit": animation.Animation(frames[:3]),
        }
        self.rect = pygame.FRect(pos, (8, 8))
        self.anim = self.anim_dict["idle"]
        self.image = self.anim.image
        self.explosion_timer = timer.Timer(1)
        self.state = "idle"
        self.player = None

    def explode(self):
        assets.sfx["explosion"].play()
        self.kill()
        x, y = int(self.rect.left / 8), int(self.rect.top / 8)
        common.current_state.sprites.add(Explosion(self.rect.topleft))
        for nx, ny in common.current_state.squares.get_neighbors((x, y), True):
            print(nx, ny)
            common.current_state.sprites.add(Explosion((nx * 8, ny * 8)))

    def update(self):
        if self.state == "idle":
            if self.player is None:
                for player in common.current_state.players:
                    if self.rect.collidepoint(player.rect.center) and player.aligned:
                        assets.sfx["pickup"].play()
                        player.set_powerup(self)
                        self.player = player
            else:
                if self.player.rect.top < 8:
                    self.rect.center = self.player.rect.midbottom
                else:
                    self.rect.center = self.player.rect.midtop
        else:
            self.explosion_timer.update()
            if not self.explosion_timer.time_left:
                self.explode()
        self.anim.update()
        self.image = self.anim.image

    def use(self):
        self.rect.center = self.player.rect.center
        self.anim = self.anim_dict["lit"]
        self.state = "lit"


class Barbwire(pygame.sprite.Sprite):
    def __init__(self, position: tuple[int, int], owner=None):
        super().__init__()
        self.live_timer = timer.Timer(7)
        self.rect = pygame.Rect(position, (8, 8))
        self.images = animation.get_spritesheet(assets.images["barbwire"])
        self.live = owner is not None
        self.image = self.images[self.live]
        self.owner = owner

    def update(self):
        for player in common.current_state.players:
            if self.rect.collidepoint(player.rect.center) and player.aligned:
                if self.live and player is not self.owner:
                    player.whack()
                if not self.live:
                    assets.sfx["barbwire"].play()
                    self.owner = player
                    self.live = True
        if self.live:
            self.live_timer.update()
            if not self.live_timer.time_left:
                self.kill()
        self.image = self.images[self.live]


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

    def reset(self):
        self.team = settings.TEAM_NONE
        self.owner = None
        self.image = self.images[self.team]

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
                if abs(nx - x) + abs(ny - y) in distances and self.is_clear_position(nx, ny):
                    yield nx, ny

    def get_sprite_by_coordinate(self, x: int, y: int) -> Square:
        return self.grid[(x, y)]

    def has_at_position(self, x, y):
        return (x, y) in self.grid

    def is_clear_position(self, x, y):
        return self.has_at_position(x, y) and self.get_sprite_by_coordinate(x, y).team in {settings.TEAM_1, settings.TEAM_2, settings.TEAM_NONE}


class Gameplay:
    POWERUPS = (Speedup, ShotGun, GasCan, Barbwire)

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
        if self.timer.time_left:
            self.sprites.update()
            self.caption_string = f"TIME: {int(self.timer.update()):02d}"
            self.powerup_timer.update()
            if not self.powerup_timer.time_left:
                self.powerup_timer.restart()
                while True:
                    spot = (random.randint(0, 7), random.randint(0, 7))
                    if self.squares.is_clear_position(*spot):
                        break
                self.sprites.add(random.choice(self.POWERUPS)((spot[0] * 8, spot[1] * 8)))

    def draw(self) -> None:
        self.sprites.draw(common.screen)

    def transition_init(self) -> None:
        # hax
        state = common.current_state
        common.current_state = self
        self.update()
        common.current_state = state

        # more hax
        screen = common.screen
        common.screen = pygame.Surface(common.screen.size)
        self.draw()
        self.____transition_image_original = self.____transition_image = common.screen
        self.____transition_image_alpha = 0
        self.____transition_image_width = 0
        common.screen = screen

    def transition_update(self) -> None:
        self.____transition_image_alpha += 80 * common.dt
        self.____transition_image_width += 30 * common.dt
        self.____transition_image_width = min(self.____transition_image_width, 64)  # nice hardcoded value
        self.____transition_image = pygame.transform.scale(
            self.____transition_image_original, (self.____transition_image_width, self.____transition_image_width)
        )
        self.____transition_image.set_alpha(self.____transition_image_alpha)

        if self.____transition_image_alpha >= 255 and self.____transition_image_width >= 64:
            common.current_state = self

    def transition_draw(self, dst: pygame.Surface) -> None:
        dst.blit(self.____transition_image, self.____transition_image.get_rect(center=pygame.Vector2(dst.size) / 2))
