import queue
import random
import pygame
from collections.abc import Iterator
from typing import Any

from .. import timer, scoreboard, particles, assets, animation, common, command, settings, utils, level, easings
from . import transition, main_menu


def center_point_collide(sprite1, sprite2):
    return sprite1.rect.collidepoint(sprite2.rect.center)


class Bullet(pygame.sprite.DirtySprite):
    SPEED = 64

    def __init__(self, pos: tuple[int, int], direction: pygame.Vector2, owner: pygame.sprite.DirtySprite):
        super().__init__()
        self.layer = 3
        self.image = pygame.Surface((1, 1))
        self.image.fill("#131313")
        self.rect = pygame.FRect(pos, (1, 1))
        self.velocity = direction.normalize() * self.SPEED
        self.owner = owner

    def update_visuals(self):
        pass

    def update(self):
        self.update_visuals()
        self.rect.center += self.velocity * common.dt
        for player in common.current_state.players:
            if player.rect.colliderect(self.rect) and player is not self.owner:
                player.whack()
                self.kill()


class Explosion(pygame.sprite.DirtySprite):
    def __init__(self, pos: tuple[int, int]):
        super().__init__()
        self.layer = 3
        common.current_state.explosions.add(self)
        self.rect = pygame.FRect(pos, (8, 8))
        self.anim = animation.NoLoopAnimation(utils.get_sprite_sheet(assets.images["explosion"]))
        self.image = self.anim.image
        self.deadly_timer = timer.Timer(0.6)

    def update_visuals(self):
        self.anim.update()
        self.image = self.anim.image

    def update(self):
        self.update_visuals()
        self.deadly_timer.update()
        x, y = int(self.rect.x / 8), int(self.rect.y / 8)
        common.current_state.squares.get_sprite_by_coordinate(x, y).reset()
        if self.deadly_timer.time_left:
            for player in common.current_state.players:
                if self.rect.collidepoint(player.rect.center):
                    player.whack()
        if self.anim.done():
            self.kill()


class Player(pygame.sprite.DirtySprite):
    SPEED = 32
    SPEEDY_SPEED = 64
    GHOST_SPEED = 32

    def __init__(self, controller: command.Controller, pos: tuple[int, int], team: int):
        super().__init__()
        self.dirty = 2
        self.layer = 3
        self.controller = controller
        self.team = team
        self.rect = pygame.FRect(0, 0, 8, 8)
        self.rect.topleft = pos
        self.moving = [0, 0]
        self.last_moving = [0, 1]
        self.command_queue = queue.Queue()
        self.squares = pygame.sprite.Group()
        self.speeding_up = False
        self.blink_timer = timer.Timer(0.1)
        self.blink_on = False
        self.strafing = False
        self.align_flag = False
        self.powerup = None
        self.spawn_point = self.rect.topleft
        self.ghost_anim = animation.SingleAnimation(assets.images["ghost"])
        self.whacked = False
        self.whacked_timer = timer.Timer(3)
        self.particle_timer = timer.Timer(0.3)
        color = {settings.TEAM_2: "2", settings.TEAM_1: "1"}[self.team]
        self.anim_dict = {
            (-1, -1): animation.Animation(utils.get_sprite_sheet(assets.images[f"Mr{color}Back"]), flip_x=True),
            (0, -1): animation.Animation(utils.get_sprite_sheet(assets.images[f"Mr{color}Back"]), flip_x=True),
            (1, -1): animation.Animation(utils.get_sprite_sheet(assets.images[f"Mr{color}Back"])),
            (1, 0): animation.Animation(utils.get_sprite_sheet(assets.images[f"Mr{color}"])),
            (1, 1): animation.Animation(utils.get_sprite_sheet(assets.images[f"Mr{color}"])),
            (0, 1): animation.Animation(utils.get_sprite_sheet(assets.images[f"Mr{color}"])),
            (-1, 1): animation.Animation(utils.get_sprite_sheet(assets.images[f"Mr{color}"]), flip_x=True),
            (-1, 0): animation.Animation(utils.get_sprite_sheet(assets.images[f"Mr{color}"]), flip_x=True),
        }
        self.controller.register_sprite(self)
        self.blank_image = pygame.Surface((0, 0))
        self.target_teams = {
            settings.TEAM_NONE,
        }
        if self.team == settings.TEAM_1:
            self.target_teams.add(settings.TEAM_2)
            self.particle_color = settings.TEAM1_COLOR
        if self.team == settings.TEAM_2:
            self.target_teams.add(settings.TEAM_1)
            self.particle_color = settings.TEAM2_COLOR

    @property
    def facing(self):
        if not pygame.Vector2(self.moving):
            return self.last_moving
        return self.moving

    @property
    def image(self):
        if self.whacked:
            image = self.ghost_anim.image.copy()
            image.set_alpha(self.whacked_timer.decimal_percent_left * 255)
            return image
        if self.speeding_up and self.blink_on:
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
        self.speeding_up = True
        self.moving = list(direction)

    def set_powerup(self, sprite):
        if self.powerup is not None:
            self.powerup.kill()
        self.powerup = sprite

    def dequip_powerup(self):
        self.powerup = None

    def whack(self):
        if not self.whacked:
            assets.sfx["whack"].play()
            if self.powerup is not None:
                self.powerup.kill()
                self.dequip_powerup()
            self.whacked = True
            self.whacked_timer.restart()
            common.current_state.kos[self.team] += 1
            self.speeding_up = False
            self.motion = [0, 0]

    def update_visuals(self):
        for anim in self.anim_dict.values():
            anim.update()
        self.ghost_anim.update()
        self.particle_timer.update()
        if not self.whacked and (pygame.Vector2(self.moving) and not self.particle_timer.time_left) or self.speeding_up:
            self.particle_timer.restart()
            lower_bound = 5
            upper_bound = 6
            for particle in particles.particle_splash(
                self.rect.center,
                self.layer - 1,
                self.particle_color,
                random.randint(lower_bound, upper_bound),
            ):
                common.current_state.sprites.add(particle)

    def update(self) -> None:
        self.update_visuals()
        if not self.whacked:
            do_shoot = False
            # Do command reading in 2 stages
            # Stage 1: realtime, cache non-realtime commands
            self.controller.update()
            while self.controller.command_queue.qsize():
                next_command = self.controller.command_queue.get()
                if next_command.command_name == command.COMMAND_SHOOT:
                    if self.powerup:
                        do_shoot = True  # defer this action until later in case other actions happen this frame
                else:
                    self.command_queue.put(next_command)
            # Stage 2: evaluate motion commands only when player is aligned with the grid
            # Ensures that the player cannot stop motion or change direction when not aligned
            last_moving = list(self.moving)
            if self.aligned and not self.speeding_up:
                while self.command_queue.qsize():
                    next_command = self.command_queue.get()
                    match next_command:
                        case command.Command(command_name=command.COMMAND_STRAFE):
                            self.strafing = True
                        case command.Command(command_name=command.COMMAND_STOP_STRAFE):
                            self.strafing = False

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
            # state handling for visuals
            if self.moving != last_moving and pygame.Vector2(last_moving):
                self.last_moving = last_moving
            # do the shoot that was deferred until later
            if do_shoot:
                self.powerup.use()
            # actual motion
            if self.strafing:
                self.moving = [0, 0]
            if self.moving[0] and self.moving[1]:
                self.moving = [self.moving[0], 0]
            speed = self.SPEED
            if self.speeding_up:
                speed = self.SPEEDY_SPEED
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
            if not pygame.Rect((0, 0, 64, 64)).contains(self.rect):
                moved = True
            if moved:
                self.speeding_up = False
                self.controller.on_motion_input()
            self.rect.clamp_ip((0, 0, 64, 64))
            self.blink_timer.update()
            if not self.blink_timer.time_left:
                self.blink_timer.restart()
                self.blink_on = not self.blink_on
        else:
            self.whacked_timer.update()
            self.ghost_anim.update()
            self.rect.topleft = pygame.Vector2(self.rect.topleft).move_towards(
                self.spawn_point, self.GHOST_SPEED * common.dt
            )
            if self.rect.topleft == self.spawn_point and not self.whacked_timer.time_left:
                self.ghost_anim.restart()
                self.controller.on_motion_input()
                self.whacked = False


class Speedup(pygame.sprite.DirtySprite):
    def __init__(self, pos: tuple[int, int]):
        super().__init__()
        self.type = level.POWERUP_SPEEDUP
        self.dirty = 2
        self.layer = 2
        self.rect = pygame.FRect(pos, (8, 8))
        x, y = int(pos[0] / 8), int(pos[1] / 8)
        anim_dict = {
            (0, -1): animation.Animation(utils.get_sprite_sheet(assets.images["speedup"])[2:]),
            (0, 1): animation.Animation(utils.get_sprite_sheet(assets.images["speedup"])[2:], flip_y=True),
            (-1, 0): animation.Animation(utils.get_sprite_sheet(assets.images["speedup"])[:2], flip_x=True),
            (1, 0): animation.Animation(utils.get_sprite_sheet(assets.images["speedup"])[:2]),
        }
        squares = common.current_state.squares
        self.coord = x, y
        self.direction = sorted(anim_dict.keys(), key=self.get_direction_score, reverse=True)[random.randint(0, 1)]
        self.anim = anim_dict[self.direction]
        self.image = self.anim.image

    def get_direction_score(self, direction):
        score = 0
        x, y = self.coord
        dx, dy = direction
        while common.current_state.squares.is_clear_position(x, y):
            x += dx
            y += dy
            score += 1
        return score

    def unused(self):
        return True  # use kills it

    def update_visuals(self):
        self.anim.update()
        self.image = self.anim.image

    def update(self):
        self.update_visuals()
        for player in common.current_state.players:
            if self.rect.collidepoint(player.rect.center) and player.aligned:
                assets.sfx["speedup"].play()
                player.speedup(self.direction)
                self.kill()


class ShotGun(pygame.sprite.DirtySprite):
    def __init__(self, pos: tuple[int, int]):
        super().__init__()
        self.type = level.POWERUP_GUN
        self.dirty = 2
        self.layer = 4
        self.image = assets.images["gun"]
        self.rect = pygame.Rect(pos, (8, 8))
        self.player = None

    def unused(self):
        return self.player is None

    def update_visuals(self):
        pass

    def update(self):
        self.update_visuals()
        if self.player is None:
            for player in common.current_state.players:
                if self.rect.collidepoint(player.rect.center) and player.aligned and not player.whacked:
                    player.set_powerup(self)
                    self.player = player
                    common.current_state.powerups.remove(self)
                    assets.sfx["pickup"].play()
        else:
            self.rect.center = self.player.rect.center

    def use(self):
        assets.sfx["gunshot"].play()
        common.current_state.sprites.add(Bullet(self.rect.center, pygame.Vector2(self.player.facing), self.player))
        self.player.dequip_powerup()
        self.kill()


class GasCan(pygame.sprite.DirtySprite):
    def __init__(self, pos: tuple[int, int]):
        super().__init__()
        self.type = level.POWERUP_GASCAN
        self.dirty = 2
        self.layer = 4
        frames = utils.get_sprite_sheet(assets.images["gascan"])
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

    def unused(self):
        return self.player is None

    def explode(self):
        assets.sfx["explosion"].play()
        self.kill()
        x, y = int(self.rect.left / 8), int(self.rect.top / 8)
        if common.current_state.squares.is_clear_position(x, y):
            common.current_state.sprites.add(Explosion((x * 8, y * 8)))
        for nx, ny in list(common.current_state.squares.get_neighbors((x, y), True)):
            common.current_state.sprites.add(Explosion((nx * 8, ny * 8)))
        common.current_state.powerups.remove(self)

    def update_visuals(self):
        self.anim.update()
        self.image = self.anim.image

    def update(self):
        if self.state == "idle":
            if self.player is None:
                for player in common.current_state.players:
                    if self.rect.collidepoint(player.rect.center) and player.aligned and not player.whacked:
                        common.current_state.powerups.remove(self)
                        assets.sfx["pickup"].play()
                        player.set_powerup(self)
                        self.player = player
            else:
                self.rect.center = self.player.rect.midtop
        else:
            self.explosion_timer.update()
            if not self.explosion_timer.time_left:
                self.explode()
        self.update_visuals()

    def use(self):
        common.current_state.powerups.add(self)
        self.player.dequip_powerup()
        self.rect.center = self.player.rect.center
        self.anim = self.anim_dict["lit"]
        self.state = "lit"


class Barbwire(pygame.sprite.DirtySprite):
    def __init__(self, position: tuple[int, int], owner=None):
        super().__init__()
        self.type = level.POWERUP_BARBWIRE
        self.dirty = 2
        self.layer = 4
        self.live_timer = timer.Timer(7)
        self.rect = pygame.Rect(position, (8, 8))
        self.images = utils.get_sprite_sheet(assets.images["barbwire"])
        self.live = owner is not None
        self.image = self.images[self.live]
        self.owner = owner

    def unused(self):
        return not self.live

    def update_visuals(self):
        self.image = self.images[self.live]

    def update(self):
        for player in common.current_state.players:
            if self.rect.collidepoint(player.rect.center) and player.aligned and not player.whacked:
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
        self.update_visuals()


class Square(pygame.sprite.DirtySprite):
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
        self.dirty = 2
        self.layer = 1
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
                    settings.TEAM_1_SPAWN,
                    settings.TEAM_2_SPAWN,
                    settings.TEAM_GRAVEL,
                ),
                utils.get_sprite_sheet(assets.images["tileset"]),
                strict=False,
            )
        )
        self.occupant = None
        self.teamchange_timer = timer.Timer(0.3)
        self._x = 0
        self._y = 0

    def reset(self):
        if self.team in {settings.TEAM_NONE, settings.TEAM_1, settings.TEAM_2}:
            self.team = settings.TEAM_NONE
            self.owner = None
            self.image = self.images[self.team]

    def update_visuals(self):
        self.image = self.images[self.team].copy()
        if self.occupant and self.teamchange_timer.time_left:
            if self.occupant.team == settings.TEAM_1:
                color = settings.TEAM1_COLOR
            else:
                color = settings.TEAM2_COLOR
            pygame.draw.line(self.image, color, (0, 8), (0, round(self.teamchange_timer.decimal_percent_left * 8)))

    def update(self) -> None:
        self.teamchange_timer.update()
        # check if I collide with any players and change color to match
        changed = False
        if self.team not in {settings.TEAM_GRAVEL, settings.TEAM_ROCK, settings.TEAM_1_SPAWN, settings.TEAM_2_SPAWN}:
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
                    if sprite is not self.occupant and not sprite.whacked:
                        self.occupant = sprite
                        self.teamchange_timer.restart()
                        if self.occupant.speeding_up:
                            self.teamchange_timer.end()
            if changed:
                # update team groups to reflect new ownership
                self.team_group.remove(self)
                self.team_group = self.team_groups[self.team]
                self.team_group.add(self)
                self.owner.squares.remove(self)
        # change color
        self.update_visuals()


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
        return self.has_at_position(x, y) and self.get_sprite_by_coordinate(x, y).team in {
            settings.TEAM_1,
            settings.TEAM_2,
            settings.TEAM_NONE,
            settings.TEAM_GRAVEL,
        }


class FOV(pygame.sprite.DirtySprite):
    def __init__(self, player):
        super().__init__()
        self.dirty = 2
        self.layer = 10  # goes over EVERYTHING
        self.rect = pygame.Rect(0, 0, 64, 64)
        self.targets = [player]
        self.surface = pygame.Surface((64, 64)).convert()
        self.fov_image = assets.images["fov"]
        self.fov_rect = self.fov_image.get_rect()
        self.blendmode = pygame.BLEND_RGB_MIN

    @property
    def image(self):
        self.surface.fill("#000000")
        for target in self.targets + list(common.current_state.explosions.sprites()):
            self.fov_rect.center = target.rect.center
            self.surface.blit(self.fov_image, self.fov_rect, None, pygame.BLEND_RGB_MAX)
        return self.surface

    def update_visuals(self):
        pass

    def update(self):
        self.update_visuals()


class Gameplay:
    STATE_START = 1
    STATE_GAMEPLAY = 2
    STATE_END = 3
    STATE_PAUSE = 4
    STATE_VICTORY = 5
    STATE_DEFEAT = 6
    STATE_COUNTDOWN = 7

    POWERUPS = {
        level.POWERUP_SPEEDUP: Speedup,
        level.POWERUP_GASCAN: GasCan,
        level.POWERUP_GUN: ShotGun,
        level.POWERUP_BARBWIRE: Barbwire,
        level.POWERUP_TORCH: Barbwire,  # FOR NOW...
    }

    def __init__(self):
        self.level_index = 0
        # timer
        self.timer = timer.Timer(64)
        self.powerup_timer = timer.Timer(2)
        self.caption_string = "TIME: 64"
        self.countdown_timer = timer.Timer(3)
        # handles level switch
        self.state = self.STATE_START
        self.scoreboard = None
        self.total_score = 0
        # sets a bunch of variables
        self.reset()

    def pause(self):
        self.state = self.STATE_PAUSE
        pygame.mixer.music.pause()
        self.scoreboard = scoreboard.ScoreBoard(self, f"PAUSED\nTime:{int(self.timer.time_left):02d}")
        self.hud.add(self.scoreboard)

    def unpause(self):
        self.state = self.STATE_GAMEPLAY
        pygame.mixer.music.unpause()

    def reset(self):
        self.level = level.LEVELS[self.level_index]
        # sprite groups
        self.sprites = pygame.sprite.LayeredDirty()
        self.powerups = pygame.sprite.Group()
        self.players = pygame.sprite.Group()
        self.hud = pygame.sprite.Group()
        self.added_scoreboard = False
        # handles squares as a graph of neighbouring sprites for BFS
        self.squares = SquareSpriteGroup()
        self.blanks = pygame.sprite.Group()
        self.team_one_squares = pygame.sprite.Group()
        self.team_two_squares = pygame.sprite.Group()
        self.explosions = pygame.sprite.Group()
        # spawn grid
        y = 0
        x = 0
        for char in self.level.world.strip():
            match char:
                case "\n":
                    y += 1
                    x = 0
                    continue
                case level.CHAR_ROCK:
                    team = settings.TEAM_ROCK
                case level.CHAR_GRAVEL:
                    team = settings.TEAM_GRAVEL
                case level.CHAR_BLANK:
                    team = settings.TEAM_NONE
                case level.CHAR_T1:
                    team = settings.TEAM_1_SPAWN
                    controller = command.InputControllerA()
                    player = Player(controller, (x * 8, y * 8), settings.TEAM_1)
                    self.sprites.add(player)
                    self.players.add(player)
                    # spawn FOV blinder (if needed)
                    if self.level.fov:
                        self.sprites.add(FOV(player))
                case level.CHAR_T2:
                    team = settings.TEAM_2_SPAWN
                    controller = command.DumbAIController(self.level.ai_dumbness)
                    player = Player(controller, (x * 8, y * 8), settings.TEAM_2)
                    self.sprites.add(player)
                    self.players.add(player)
            sprite = Square(
                (x * 8, y * 8), self.players, self.blanks, self.team_one_squares, self.team_two_squares, team
            )
            self.sprites.add(sprite)
            self.squares.add_to_grid(sprite, x, y)
            x += 1
        # set game values
        self.kos = {
            settings.TEAM_1: 0,
            settings.TEAM_2: 0,
        }
        self.state = self.STATE_START
        # create scoreboard
        self.scoreboard = scoreboard.ScoreBoard(self, self.level.remark)
        self.hud.add(self.scoreboard)
        # timer stuff
        self.timer.restart()
        self.powerup_timer.restart()
        # Jiffy's turn for some hax code
        state = common.current_state
        common.current_state = self
        self.sprites.update()
        common_current_state = state
        self.transition_easers: dict[Any, easings.EasyScalar] = {}

    def get_winner(self):
        return list(
            sorted((settings.TEAM_1, settings.TEAM_2), key=lambda x: self.get_square_count(x) - self.get_ko_count(x))
        )[-1]

    def get_square_count(self, team):
        count = 0
        for square in self.squares.sprites():
            if square.team == team:
                count += 1
        return count

    def get_ko_count(self, team):
        return self.kos[team]

    def can_put_powerup_in_spot(self, spot):
        center = (spot[0] * 8 + 4, spot[1] * 8 + 4)
        if not self.squares.is_clear_position(*spot):
            return False
        for sprite in self.powerups:
            if sprite.rect.collidepoint((center)):
                return False
        return True

    def update(self) -> None:
        self.countdown_timer.update()
        if self.state == self.STATE_GAMEPLAY:
            if not self.timer.time_left:
                self.state = self.STATE_END
                self.scoreboard = scoreboard.ScoreBoard(self)
                self.hud.add(self.scoreboard)
            self.sprites.update()
            self.caption_string = f"TIME: {int(self.timer.update()):02d}"
            self.powerup_timer.update()
            if (not self.powerup_timer.time_left) and self.level.powerups:
                self.powerup_timer.restart()
                for i in range(30):
                    spot = (random.randint(0, 7), random.randint(0, 7))
                    if self.can_put_powerup_in_spot(spot):
                        break
                powerup = self.POWERUPS[random.choice(self.level.powerups)]((spot[0] * 8, spot[1] * 8))
                self.sprites.add(powerup)
                self.powerups.add(powerup)
            for event in common.events:
                if event.type == pygame.KEYDOWN and event.key == pygame.K_e:
                    self.pause()
        elif self.state == self.STATE_START:
            if self.scoreboard.done:
                self.state = self.STATE_COUNTDOWN
                self.scoreboard = scoreboard.Countdown()
                self.hud.add(self.scoreboard)
                pygame.mixer.music.load(assets.ost_path("SquareWarsBattle"))
                pygame.mixer.music.play()
        elif self.state == self.STATE_COUNTDOWN:
            if self.scoreboard.done:
                self.state = self.STATE_GAMEPLAY
        elif self.state == self.STATE_END:
            if self.scoreboard.done:
                self.level_index += 1
                self.total_score += self.get_square_count(settings.TEAM_1) - self.get_ko_count(settings.TEAM_1)
                if self.get_winner() != settings.TEAM_1:
                    self.state = self.STATE_DEFEAT
                    self.scoreboard = scoreboard.ScoreBoard(self, f"Failure.\n{self.total_score}pts")
                    self.hud.add(self.scoreboard)
                elif self.level_index >= len(level.LEVELS):
                    self.state = self.STATE_VICTORY
                    self.scoreboard = scoreboard.ScoreBoard(self, f"Victory!\n{self.total_score}pts")
                    self.hud.add(self.scoreboard)
                else:
                    self.reset()
        elif self.state == self.STATE_PAUSE:
            if self.scoreboard.done:
                self.unpause()
        elif self.state in {self.STATE_VICTORY, self.STATE_DEFEAT}:
            if self.scoreboard.done:
                pygame.event.post(pygame.Event(pygame.KEYDOWN, key=pygame.K_ESCAPE))
                pygame.event.post(pygame.Event(pygame.KEYUP, key=pygame.K_ESCAPE))
        self.hud.update()

    def draw(self, surface=None) -> None:
        if surface is None:
            surface = common.screen
        self.sprites.draw(surface)
        self.hud.draw(surface)

    def transition_init(self) -> None:
        # hax
        state = common.current_state
        common.current_state = self
        common.current_state = state

        # more hax
        screen = common.screen
        common.screen = pygame.Surface(common.screen.get_size())
        self.draw()
        self.____transition_image_original = self.____transition_image = common.screen
        self.____transition_image_alpha = 0
        self.____transition_image_width = 0
        common.screen = screen

        self.transition_easers["size"] = easings.EasyScalar(easings.in_bounce, 0, 64, 3)

    def transition_update(self) -> None:
        for easer in self.transition_easers.values():
            easer.update()

        self.____transition_image_alpha += 80 * common.dt
        # self.____transition_image_width += 30 * common.dt
        # self.____transition_image_width = min(self.____transition_image_width, 64)  # nice hardcoded value
        self.____transition_image_width = self.transition_easers["size"].current
        self.____transition_image = pygame.transform.scale(
            self.____transition_image_original, (self.____transition_image_width, self.____transition_image_width)
        )
        self.____transition_image.set_alpha(self.____transition_image_alpha)

        if self.____transition_image_alpha >= 255 and self.____transition_image_width >= 64:
            common.current_state = self

    def transition_draw(self, dst: pygame.Surface) -> None:
        dst.blit(
            self.____transition_image, self.____transition_image.get_rect(center=pygame.Vector2(dst.get_size()) / 2)
        )
