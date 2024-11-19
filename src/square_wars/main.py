import pygame
import pygame._sdl2 as pg_sdl2  # noqa

from . import common, settings, assets, states

pygame.init()
common.screen = screen = pygame.display.set_mode(settings.LOGICAL_SIZE, flags=settings.DISPLAY_FLAGS | pygame.HIDDEN)
common.clock = clock = pygame.Clock()

window = pygame.Window.from_display_module()
if settings.FULLSCREEN:
    window.set_fullscreen(True)
window.show()

if any(settings.DISPLAY_FLAGS & flag for flag in [pygame.SCALED, pygame.OPENGL, pygame.DOUBLEBUF]):
    renderer = pg_sdl2.Renderer.from_window(window)
else:
    renderer = pg_sdl2.Renderer(window)
renderer.draw_color = "#b22222"

assets.load_assets()

common.current_state = states.Gameplay()
# common.current_state = states.MainMenu()

running = True
while running:
    dt = clock.tick(settings.FPS) / 1000
    common.dt = dt = pygame.math.clamp(dt, 0.0005, 0.05)
    pygame.display.set_caption(f"{settings.TITLE} | FPS: {clock.get_fps():.0f} | {common.current_state.caption_string}")

    screen.fill("black")

    events = pygame.event.get()
    common.events = events
    for event in events:
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                common.current_state = states.Gameplay()

    common.current_state.update()
    common.current_state.draw()

    pygame.display.flip()
