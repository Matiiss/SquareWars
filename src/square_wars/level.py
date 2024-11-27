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


@dataclass(frozen=True)
class Level:
    remark: str
    powerups: list
    ai_dumbness: int
    world: str
    fov: bool = False

    
TUTORIAL = Level(
    remark="Move:\n WASD\nPause:\n e",
    powerups=(POWERUP_SPEEDUP,),
    ai_dumbness=25,
    world="""
1.......
......%.
....#%%.
........
.#......
...#.%..
.%......
..#....2
""",
)

TUTORIAL_GUN = Level(
    remark="Use pickup\n with 'q'.\nDon't get\nshot!",
    powerups=[POWERUP_SPEEDUP, POWERUP_GUN],
    ai_dumbness=20,
    world="""
1.......
..#...#.
#.......
..#.#%..
...#%#..
.......#
.#...#%%
......%2
""",
)

TUTORIAL_GASCAN = Level(
    remark="Use a\nGAS CAN\nand run.\nBOOM!",
    powerups=(POWERUP_GASCAN,),
    ai_dumbness=10,
    world="""
1.......
........
........
........
........
........
........
.......2
""",
)

TUTORIAL_BARBWIRE = Level(
    remark="Barbwire:\nsafe if you\ntouch it\nfirst.",
    powerups=(POWERUP_BARBWIRE,),
    ai_dumbness=7,
    world="""
2.#.#.#.
........
#.#.#.#.
........
#.#.#.#.
........
#.#.#.#.
.......1
"""
)

TWO_OPPONENT = Level(
    remark="One guy...\nToo easy.",
    powerups=(POWERUP_GUN, POWERUP_GASCAN, POWERUP_SPEEDUP),
    ai_dumbness=40,
    world="""
2.......
#...###.
........
.#.#1...
##.###.#.
....#...
.#.....#
.#.....2
""",
)

DUEL = Level(
    remark="Unless...\nit's THIS\nguy!",
    powerups=(POWERUP_GUN, POWERUP_SPEEDUP, POWERUP_GASCAN),
    ai_dumbness=0,
    world="""
1.......
.##..##.
.#....#.
...##...
...##...
.#....#.
.##..##.
.......2
""",
)

DARK = Level(
    remark="Night\nFalls...",
    powerups=(POWERUP_TORCH, POWERUP_BARBWIRE, POWERUP_GUN),
    ai_dumbness=10,
    world="""
1.......
#.#.#.#.
........
.#.#.#.#
........
#.#.#.#.
........
.#.#.#2#
""",
    fov=True,
)

BOMBERMAN = Level(
    remark="Gas-\nlightinng...",
    powerups=(POWERUP_GASCAN,),
    ai_dumbness=0,
    world="""
1%.%.%.%
%.%.%.%.
.%.%.%.%
%.%.%.%.
.%.%.%.%
%.%.%.%.
.%.%.%.%
%.%.%.%2
""",
    fov=True,
)

DOUBLE_TROUBLE = Level(
    remark="Double\nTrouble",
    powerups=(POWERUP_GUN, POWERUP_SPEEDUP, POWERUP_BARBWIRE, POWERUP_GASCAN),
    ai_dumbness=20,
    world="""
........
.##...#.
.%%%%%#.
...12...
...21...
.#%%%%%.
.#...##.
........
"""
)

TIME_TRIALS = Level(
    remark="Are you\nFAST\nenough?",
    powerups=(POWERUP_GUN,),
    ai_dumbness=0,
    world="""
1.......
.#.####.
...#....
#.#.....
.....#.#
....#...
.####.#.
.......2
""",
)

DEATH = Level(
    remark="You won't\nbeat this.",
    powerups=(POWERUP_SPEEDUP, POWERUP_BARBWIRE, POWERUP_GASCAN, POWERUP_GUN),
    ai_dumbness=80,
    world="""
1%%..%%2
%##%%##%
%#....#%
.%....%.
.%....%.
%#....#%
%##%%##%
2%%..%%2
""",
    fov=False,
)

PUZZLE = Level(
    remark="This one\nuses your\nbrain.",
    powerups=(POWERUP_SPEEDUP, POWERUP_GASCAN, POWERUP_GUN, POWERUP_BARBWIRE),
    ai_dumbness=0,
    world="""
1...1...
##..##..
.##...#.
....#.#.
###.###.
..#...#.
#.......
..##2##.
"""
)

NIGHT_CRAWLING = Level(
    remark="Night\nCrawling",
    powerups=(POWERUP_GASCAN, POWERUP_GUN, POWERUP_BARBWIRE),
    ai_dumbness=5,
    world="""
........
.....%..
..2..%..
........
........
....1...
........
..%.....
""",
    fov=True,
)

LEVELS = (
    TUTORIAL,
    TUTORIAL_GUN,
    TUTORIAL_GASCAN,
    TUTORIAL_BARBWIRE,
    TWO_OPPONENT,
    DUEL,
    DARK,
    DOUBLE_TROUBLE,
    NIGHT_CRAWLING,
    BOMBERMAN,
    PUZZLE,
    TIME_TRIALS,
    DEATH,
)
