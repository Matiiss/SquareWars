import pygame

from . import proto

screen: pygame.Surface

dt: float
events: list[pygame.Event]
clock: pygame.Clock

current_state: proto.State
