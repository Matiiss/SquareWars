import asyncio
import platform

import pygame
import pygame._sdl2 as pg_sdl2  # noqa

from . import common, settings, assets, states, event_types

if settings.PYGBAG:
    platform.window.canvas.style.imageRendering = "pixelated"


async def run():
    await asyncio.sleep(0)
    pygame.init()
    await assets.load_async()

    icon = assets.load_image_raw("icon")
    pygame.display.set_icon(icon)
    common.screen = pygame.display.set_mode(settings.LOGICAL_SIZE, flags=settings.DISPLAY_FLAGS | pygame.HIDDEN)
    common.clock = clock = pygame.Clock()

    common.window = pygame.Window.from_display_module()
    if settings.FULLSCREEN:
        common.window.set_fullscreen(True)
    common.window.show()
    if not settings.PYGBAG:
        if any(settings.DISPLAY_FLAGS & flag for flag in [pygame.SCALED, pygame.OPENGL, pygame.DOUBLEBUF]):
            renderer = pg_sdl2.Renderer.from_window(common.window)
        else:
            renderer = pg_sdl2.Renderer(common.window)
        renderer.draw_color = "#391f21"
    # common.current_state = states.Gameplay()
    common.current_state = states.MainMenu()
    pygame.display.set_caption("Square Wars")

    prev_sfx_volume = common.sfx_volume
    prev_music_volume = common.music_volume

    running = True
    while running:
        dt = clock.tick(settings.FPS * (not settings.PYGBAG)) / 1000
        common.dt = dt = pygame.math.clamp(dt, 0.0005, 0.05)
        if not settings.PYGBAG:
            pygame.display.set_caption(
                f"{settings.TITLE} | FPS: {clock.get_fps():.0f} | {common.current_state.caption_string}"
            )

        common.screen.fill("black")
        common.events = pygame.event.get()
        for event in common.events:
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if not settings.PYGBAG and isinstance(common.current_state, states.MainMenu):
                        running = False
                    else:
                        common.current_state = states.MainMenu()
            elif event.type == event_types.SWITCH_TO_GAMEPLAY:
                common.current_state = states.Gameplay()

        common.current_state.update()
        common.current_state.draw()

        if prev_sfx_volume != common.sfx_volume:
            assets.set_sound_volume(common.sfx_volume)
            prev_sfx_volume = common.sfx_volume

        if prev_music_volume != common.music_volume:
            pygame.mixer.music.set_volume(common.music_volume)
            prev_music_volume = common.music_volume

        pygame.display.flip()
        await asyncio.sleep(0)

    pygame.quit()


if __name__ == "__main__":
    try:
        asyncio.run(run())
    except ValueError:
        # I don't know how else to handle "a coroutine was expected, got None" (yet)
        raise SystemExit from None
