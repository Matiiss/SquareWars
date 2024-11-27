import pygame

from . import proto

screen: pygame.Surface

dt: float
events: list[pygame.Event]
clock: pygame.Clock

current_state: proto.State

music_volume: float = 0.5
sfx_volume: float = 0.5
