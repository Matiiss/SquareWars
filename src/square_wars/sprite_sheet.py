import json
import collections
import pathlib
import operator

import pygame


class AsepriteSpriteSheet:
    def __init__(self, sheet_path, config_path=None):
        sheet_path = pathlib.Path(sheet_path)
        if config_path is None:
            config_path = pathlib.Path(sheet_path.parent, f"{sheet_path.stem}.json")
        with open(config_path) as file:
            config = json.load(file)

        self._data = collections.defaultdict(list)

        sprite_sheet = pygame.image.load(sheet_path).convert_alpha()
        for name, data in config["frames"].items():
            key, num = name.rsplit("_", maxsplit=1)
            x, y, w, h = data["frame"].values()
            image = sprite_sheet.subsurface((x, y, w, h))
            self._data[key].append((int(num), {"image": image, "duration": data["duration"]}))

        get_first = operator.itemgetter(0)
        for key, value in self._data.items():
            self._data[key] = [tpl[1] for tpl in sorted(value, key=get_first)]

    def __getitem__(self, item):
        return self._data[item]

    @property
    def data(self):
        return self._data
