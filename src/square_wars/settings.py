import pygame

TITLE = "Square Wars"

LOGICAL_WIDTH = 64
LOGICAL_HEIGHT = 64
LOGICAL_SIZE = (LOGICAL_WIDTH, LOGICAL_HEIGHT)

DISPLAY_FLAGS = pygame.SCALED
FULLSCREEN = False

TEAM_NONE = -1
TEAM_1 = 0
TEAM_2 = 1
TEAM_ROCK = 2
TEAM_1_SPAWN = 3
TEAM_2_SPAWN = 4

BLANK_COLOR = "#d4d3d1"
TEAM1_COLOR = "#db4b16"
TEAM2_COLOR = "#ffb938"

MR1_CHAR = "~"
MR2_CHAR = "`"
TEAM1_TILE_CHAR = "@"
TEAM2_TILE_CHAR = "#"
TEAM1_KO_CHAR = "$"
TEAM2_KO_CHAR = "%"

FONT_SIZE = 8

FPS = 60
