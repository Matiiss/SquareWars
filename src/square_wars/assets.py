from pathlib import Path

import pygame

ASSETS_DIR = Path("assets")

images: dict = {}
sfx: dict[str, pygame.mixer.Sound] = {}


def image_path(path, extension="png"):
    return ASSETS_DIR / "images" / f"{path}.{extension}"


def load_image(path):
    return pygame.image.load(image_path(path))


def load_sound(path, extension="mp3"):
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
            # "image": load_image("image"),
        }
    )
    sfx.update(
        {
            # "sfx": load_sound("sfx")
        }
    )
