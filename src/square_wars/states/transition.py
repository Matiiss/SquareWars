import pygame

from .. import proto, common


class Transition:
    caption_string = ""

    def __init__(self, current_state: proto.State, next_state: proto.State) -> None:
        current_state.transition_init()
        next_state.transition_init()

        self.current_state = current_state
        self.next_state = next_state

    def update(self) -> None:
        self.current_state.transition_update()
        self.next_state.transition_update()

    def draw(self) -> None:
        current_surf = pygame.Surface(common.screen.get_size(), flags=pygame.SRCALPHA)
        self.current_state.transition_draw(current_surf)

        next_surf = pygame.Surface(common.screen.get_size(), flags=pygame.SRCALPHA)
        self.next_state.transition_draw(next_surf)

        common.screen.blit(next_surf, (0, 0))
        common.screen.blit(current_surf, (0, 0))
