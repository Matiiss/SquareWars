from pathlib import Path

import pygame
import asyncio

from . import settings

if settings.PYGBAG:
    ASSETS_DIR = Path("res")
    AUDIO_EXTENSION = "ogg"
else:
    ASSETS_DIR = Path("src/res")
    AUDIO_EXTENSION = "wav"

images: dict[str, pygame.Surface] = {}
sfx: dict[str, pygame.mixer.Sound] = {}
fonts: dict[str, pygame.font.Font] = {}

def image_path(path, extension="png"):
    return ASSETS_DIR / "images" / f"{path}.{extension}"


def ost_path(path, extension=AUDIO_EXTENSION):
    return ASSETS_DIR / "ost" / f"{path}.{extension}"


def load_image_raw(path) -> pygame.Surface:
    return pygame.image.load(image_path(path))


def load_image(path):
    return load_image_raw(path).convert_alpha()


def load_sound(path, extension=AUDIO_EXTENSION):
    return pygame.mixer.Sound(ASSETS_DIR / "sfx" / f"{path}.{extension}")


def load_font(path, extension="ttf"):
    return pygame.font.Font(ASSETS_DIR / f"{path}.{extension}", size=settings.FONT_SIZE)


def set_sound_volume(value):
    for sound in sfx.values():
        sound.set_volume(value)


# how does one... resume them?
def stop_all_sounds():
    for sound in sfx.values():
        sound.stop()


def load_assets():
    images.update(
        {
            "Mr1": load_image("Mr1"),
            "Mr1Back": load_image("Mr1Back"),
            "Mr2": load_image("Mr2"),
            "Mr2Back": load_image("Mr2Back"),
            "tileset": load_image("tileset"),
            "speedup": load_image("speedup"),
            "menu_bg": load_image("main_menu_bg"),
            "selector_arrow": load_image("selector_arrow"),
            "play_button": load_image("play_button"),
            "settings_button": load_image("settings_button"),
            "menu_title": load_image("menu_title"),
            "gun": load_image("gun"),
            "ghost": load_image("ghost"),
            "gascan": load_image("gascan"),
            "explosion": load_image("explosion"),
            "barbwire": load_image("barbwire"),
            "ko": load_image("ko"),
            "guiWoodBG": load_image("guiWoodBG"),
            "clouds": load_image("clouds"),
            "fov": load_image("fov"),
            "countdown": load_image("countdown"),
        }
    )
    sfx.update(
        {
            "barbwire": load_sound("barbwire"),
            "grass": load_sound("grass"),
            "gunshot": load_sound("gunshot"),
            "pickup": load_sound("pickup"),
            "select": load_sound("select"),
            "switch": load_sound("switch"),
            "whack": load_sound("whack"),
            "explosion": load_sound("explosion"),
            "speedup": load_sound("speedup"),
        }
    )
    fonts.update({"silkscreen": load_font("silkfont"), "silkscreen-bold": load_font("silkfont-bold")})


async def load_async():
    flags = 0
    if not settings.PYGBAG:
        flags = pygame.NOFRAME | pygame.SCALED
    screen = pygame.display.set_mode((64, 64), flags)
    screen.fill("white")
    logo = load_image("logo")
    logo_rect = logo.get_rect()
    logo_rect.center = (32, 32)
    screen.blit(logo, logo_rect)
    pygame.display.update()
    await asyncio.sleep(0)
    load_assets()
    await asyncio.sleep(2)
    print("after sleep")