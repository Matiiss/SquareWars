from pathlib import Path

import pygame

ASSETS_DIR = Path("res")

images: dict[str, pygame.Surface] = {}
sfx: dict[str, pygame.mixer.Sound] = {}


def image_path(path, extension="png"):
    return ASSETS_DIR / "images" / f"{path}.{extension}"


def ost_path(path, extension="wav"):
    return ASSETS_DIR / "ost" / f"{path}.{extension}"


def load_image_raw(path) -> pygame.Surface:
    return pygame.image.load(image_path(path))


def load_image(path):
    return load_image_raw(path).convert_alpha()


def load_sound(path, extension="wav"):
    return pygame.mixer.Sound(ASSETS_DIR / "sfx" / f"{path}.{extension}")


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
            "barbwire": load_image("barbwire")
        }
    )
    sfx.update(
        {
            # "sfx": load_sound("sfx")
        }
    )
