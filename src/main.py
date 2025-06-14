import pygame
import sys
from game.settings import Settings
from game.game_state import GameStateManager
from utils.constants import WINDOW_WIDTH, WINDOW_HEIGHT, FPS


def main():
    pygame.init()

    # Window setup
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("MIPY Game")
    clock = pygame.time.Clock()

    # Init game systems
    settings = Settings()
    game_state_manager = GameStateManager()

    # Main game loop
    running = True
    while running:
        dt = clock.tick(FPS) / 1000.0

        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            game_state_manager.handle_event(event)

        # Update
        game_state_manager.update(dt)

        # Render
        screen.fill((0, 0, 0))
        game_state_manager.render(screen)
        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()