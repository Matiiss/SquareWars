import pygame

from dataclasses import dataclass

POWERUP_SPEEDUP = 1
POWERUP_GUN = 2
POWERUP_GASCAN = 3
POWERUP_BARBWIRE = 4
POWERUP_TORCH = 5

CHAR_BLANK = "."
CHAR_T1 = "1"
CHAR_T2 = "2"
CHAR_ROCK = "#"
CHAR_GRAVEL = "%"

@dataclass
class Level:
    remark: str
    powerups: list
    ai_dumbness: int
    world: str
    fov: bool = False
    
LEVEL_1 = Level(
    remark="Move:\nWASD\nPause:\ne",
    powerups=(POWERUP_SPEEDUP,),
    ai_dumbness=25,
    world="""
1.......
........
....#...
........
.#......
...#....
........
..#....2
"""
)

LEVEL_2 = Level(
    remark="Shoot:\nq\n",
    powerups=(POWERUP_SPEEDUP, POWERUP_GUN),
    ai_dumbness=20,
    world="""
1.......
..#...#.
#.......
..###...
...###..
.......#
.#...#..
.......2
"""
)

LEVELS = (
    LEVEL_1,
    LEVEL_2,
)