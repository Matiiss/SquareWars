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
    common.screen = screen = pygame.display.set_mode(settings.LOGICAL_SIZE, flags=settings.DISPLAY_FLAGS | pygame.HIDDEN)
    common.clock = clock = pygame.Clock()

    window = pygame.Window.from_display_module()
    if settings.FULLSCREEN:
        window.set_fullscreen(True)
    window.show()
    if not settings.PYGBAG:
        if any(settings.DISPLAY_FLAGS & flag for flag in [pygame.SCALED, pygame.OPENGL, pygame.DOUBLEBUF]):
            renderer = pg_sdl2.Renderer.from_window(window)
        else:
            renderer = pg_sdl2.Renderer(window)
        renderer.draw_color = "#391f21"
    # common.current_state = states.Gameplay()
    common.current_state = states.MainMenu()
    pygame.display.set_caption("Square Wars")

    running = True
    while running:
        dt = clock.tick(settings.FPS * (not settings.PYGBAG)) / 1000
        common.dt = dt = pygame.math.clamp(dt, 0.0005, 0.05)
        if not settings.PYGBAG:
            pygame.display.set_caption(f"{settings.TITLE} | FPS: {clock.get_fps():.0f} | {common.current_state.caption_string}")

        screen.fill("black")
        events = pygame.event.get()
        common.events = list(events)
        for event in common.events:
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if not settings.PYGBAG and isinstance(common.current_state, states.MainMenu):
                        pygame.quit()
                    common.current_state = states.MainMenu()
            elif event.type == event_types.SWITCH_TO_GAMEPLAY:
                common.current_state = states.Gameplay()

        common.current_state.update()
        common.current_state.draw()

        pygame.display.flip()
        await asyncio.sleep(0)

if __name__ == "__main__":
    asyncio.run(run())