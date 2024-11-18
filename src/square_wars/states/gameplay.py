import queue
import pygame

from .. import settings
from .. import command
from .. import common

def center_point_collide(sprite1, sprite2):
    return sprite1.rect.collidepoint(sprite2.rect.center)

class Player(pygame.sprite.Sprite):
    SPEED = 8

    def __init__(self, controller, pos, team):
        super().__init__()
        self.controller = controller
        self.image = pygame.Surface((8, 8)).convert()
        self.team = team
        self.rect = pygame.FRect(0, 0, 8, 8)
        self.rect.topleft = pos
        self.moving = [0, 0]
        self.facing = [0, 0]
        self.command_queue = queue.Queue()

    def update(self):
        self.controller.update()
        while self.controller.command_queue.qsize():
            next_command = self.controller.command_queue.get()
            if next_command.command_name == command.COMMAND_SHOOT:
                print("pew pew")
            else:
                self.command_queue.put(next_command)
        if int(self.rect.x) % 8 == 0 and int(self.rect.y) % 8 == 0:
            # self.rect.x = int(self.rect.x)
            # self.rect.y = int(self.rect.y)
            while self.command_queue.qsize():
                next_command = self.command_queue.get()
                match next_command:
                    case command.Command(command_name=command.COMMAND_UP):
                        self.moving[1] -= 1
                        self.facing[1] = -1
                    case command.Command(command_name=command.COMMAND_STOP_UP):
                        self.moving[1] += 1
                    
                    case command.Command(command_name=command.COMMAND_DOWN):
                        self.moving[1] += 1
                        self.facing[1] = 1
                    case command.Command(command_name=command.COMMAND_STOP_DOWN):
                        self.moving[1] -= 1
                    
                    case command.Command(command_name=command.COMMAND_LEFT):
                        self.moving[0] -= 1
                        self.facing[0] = -1
                    case command.Command(command_name=command.COMMAND_STOP_LEFT):
                        print("left stop")
                        self.moving[0] += 1
                    
                    case command.Command(command_name=command.COMMAND_RIGHT):
                        self.moving[0] += 1
                        self.facing[0] = 1
                    case command.Command(command_name=command.COMMAND_STOP_RIGHT):
                        self.moving[0] -= 1

        print(self.moving)
                
        if pygame.Vector2(self.moving):
            self.velocity = pygame.Vector2(self.moving)
            self.velocity.scale_to_length(self.SPEED)
        else:
            self.velocity = pygame.Vector2()
        self.rect.center += self.velocity * common.dt
        self.rect.clamp_ip((0, 0, 64, 64))


class Square(pygame.sprite.Sprite):
    def __init__(self, pos, player_group):
        super().__init__()
        self.rect = pygame.FRect(0, 0, 8, 8)
        self.rect.topleft = pos
        self.player_group = player_group
        self.team = settings.TEAM_NONE
        self.owner = None
        self.image = pygame.Surface((8, 8)).convert()
        self.image.fill(settings.BLANK_COLOR)

    def update(self):
        changed = False
        for sprite in pygame.sprite.spritecollide(self, self.player_group, False, center_point_collide):
            if sprite is not self.owner:
                self.team = sprite.team
                self.owner = sprite
                changed = True
        if changed:
            if self.team == settings.TEAM_BROWN:
                color = settings.BROWN_COLOR
            if self.team == settings.TEAM_ORANGE:
                color = settings.ORANGE_COLOR
            if self.team == settings.TEAM_NONE:
                color = settings.BLANK_COLOR
            self.image.fill(color)



class Gameplay:
    def __init__(self):
        self.sprites = pygame.sprite.Group()
        self.players = pygame.sprite.Group()
        for x in range(0, 64, 8):
            for y in range(0, 64, 8):
                self.sprites.add(Square((x, y), self.players))
        controller = command.InputController()
        player = Player(controller, (0, 0), settings.TEAM_ORANGE)
        self.sprites.add(player)
        self.players.add(player)

    def update(self) -> None:
        self.sprites.update()


    def draw(self) -> None:
        self.sprites.draw(common.screen)
