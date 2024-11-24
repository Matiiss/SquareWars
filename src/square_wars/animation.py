from . import common, utils


class Animation:
    def __init__(self, frames, speed=0.2, flip_x=False, flip_y=False):
        self.frames = list(frames)
        self.time = 0
        self.speed = speed
        self.flip_x = flip_x
        self.flip_y = flip_y

    def update(self):
        self.time += common.dt

    def restart(self):
        self.time = 0

    @property
    def image(self):
        image = self.frames[round(self.time / self.speed) % len(self.frames)]
        return utils.flip_surface(image, self.flip_x, self.flip_y)


class NoLoopAnimation:
    def __init__(self, frames, speed=0.2, flip_x=False, flip_y=False):
        self.frames = list(frames)
        self.time = 0
        self.speed = speed
        self.flip_x = flip_x
        self.flip_y = flip_y

    def update(self):
        self.time += common.dt

    def restart(self):
        self.time = 0

    def done(self):
        return min(round(self.time / self.speed), len(self.frames) - 1) == len(self.frames) - 1

    @property
    def image(self):
        frame_index = min(round(self.time / self.speed), len(self.frames) - 1)
        return utils.flip_surface(self.frames[frame_index], self.flip_x, self.flip_y)


class SingleAnimation:
    def __init__(self, surface, flip_x=False, flip_y=False):
        self.surface = surface
        self.flip_x = flip_x
        self.flip_y = flip_y

    def update(self):
        pass

    def restart(self):
        pass

    @property
    def image(self):
        return utils.flip_surface(self.surface, self.flip_x, self.flip_y)
