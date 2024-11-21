import itertools

import pygame

pygame.init()

FONTTYPE_BOLD = 1
FONTTYPE_ITALIC = 2
FONTTYPE_UNDERLINE = 4
FONTTYPE_STRIKETHROUGH = 8

FLOAT_INLINE = 0
FLOAT_BREAK = 1
FLOAT_BREAK_CENTER = 2
FLOAT_BREAK_RIGHT = 3


class FontHolder:
    def __init__(self, name, size):
        self.fonts = {}
        for i in range(16):
            self.fonts[i] = pygame.font.SysFont(name, size, i & FONTTYPE_BOLD, i & FONTTYPE_ITALIC)
            self.fonts[i].underline = i & FONTTYPE_UNDERLINE
            self.fonts[i].strikethrough = i & FONTTYPE_STRIKETHROUGH

    def __getitem__(self, item):
        return self.fonts[item]


class Chunk(pygame.sprite.Sprite):
    def __init__(self, image, float_method=FLOAT_INLINE):
        self.image = image
        self.rect = self.image.get_rect()
        self.float_method = float_method
        super().__init__()

    def position(self, previous_rect, force_break, max_width):
        self.rect.topleft = previous_rect.topright
        if (self.rect.right > max_width) or self.float_method or force_break:
            self.rect.left = (0, 0, (max_width - self.rect.width) // 2, max_width - self.rect.width)[self.float_method]
            self.rect.top += 1

    def set_layers(self, layer_tops, line_heights):
        self.rect.top = layer_tops[self.rect.top] + ((line_heights[self.rect.top] - self.rect.height) // 2)


class LineBreak(Chunk):
    def __init__(self):
        super().__init__(pygame.Surface((0, 0)))

    def position(self, previous_rect, force_break, max_width):
        super().position(previous_rect, True, max_width)


class TextChunk(Chunk):
    font_data = {
        "default-16": FontHolder("arial", 16)
    }

    def __init__(self, text, fonttype=0, fontname="default", fontsize=16, fontcolor='black', bgcolor=None):
        fontkey = f"{fontname}-{fontsize}"
        if fontkey in self.font_data:
            font = self.font_data[fontkey][fonttype]
        else:
            holder = FontHolder(fontname, fontsize)
            self.font_data[fontkey] = holder
            font = holder[fonttype]
        super().__init__(font.render(text, True, fontcolor, bgcolor))


class ChunkRenderer(pygame.sprite.Sprite):
    def __init__(self, chunks, max_width, dynamic=False):
        self.chunk_group = pygame.sprite.Group(chunks)
        self.max_width = max_width
        self.dynamic = dynamic
        # these vars set on rebuild
        self.image = None
        self.rect = None
        self.rebuild()
        super().__init__()

    def rebuild(self):
        layers = [0]
        line_heights = []
        previous_rect = pygame.Rect(0, 0, 0, 0)
        current_row = []
        height = 0
        force_break = 0
        for sprite in self.chunk_group:
            # position sprite
            sprite.position(previous_rect, force_break, self.max_width)
            force_break = sprite.float_method
            # if sprite is on a new row, position the last row, reset the row list
            if sprite.rect.top != previous_rect.top:
                max_height = 0
                for row_sprite in current_row:
                    max_height = max(row_sprite.rect.height, max_height)
                layers.append(layers[-1] + max_height)
                line_heights.append(max_height)
                height += max_height
                current_row = []
            # add the sprite to the current row
            current_row.append(sprite)
            previous_rect = sprite.rect
        # position the final row
        max_height = 0
        for row_sprite in current_row:
            max_height = max(row_sprite.rect.height, max_height)
        layers.append(layers[-1] + max_height)
        height += max_height
        line_heights.append(max_height)
        for sprite in self.chunk_group:
            sprite.set_layers(layers, line_heights)
        self.rect = pygame.Rect(0, 0, self.max_width, height)
        self.image = pygame.Surface(self.rect.size, pygame.SRCALPHA).convert_alpha()
        self.chunk_group.draw(self.image)

    def update(self, dt=None):
        if self.dynamic:
            self.rebuild()

    def move(self, offset):
        self.rect.topleft = pygame.Vector2(self.rect.topleft) + offset

    def move_to(self, pos):
        self.rect.topleft = pos