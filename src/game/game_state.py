import pygame
from entities.player import Player
from utils.constants import (
    WINDOW_WIDTH, WINDOW_HEIGHT, DOT_SIZE, DOT_SPACING, 
    GRAY, CAMERA_LERP, BLACK
)


class GameState:
    """Base class for game states"""

    def handle_event(self, event):
        """Event processing"""
        pass

    def update(self, dt):
        """State update"""
        pass

    def render(self, screen):
        """State rendering"""
        pass


class MenuState(GameState):
    """Main menu"""

    def __init__(self):
        self.font = pygame.font.Font(None, 74)
        self.title_text = self.font.render("DEADLOCK", True, (255, 255, 255))
        self.subtitle_font = pygame.font.Font(None, 36)
        self.subtitle_text = self.subtitle_font.render("Press SPACE to start", True, (200, 200, 200))

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                # Přepnout na gameplay
                return "gameplay"
        return None

    def render(self, screen):
        screen_rect = screen.get_rect()
        title_rect = self.title_text.get_rect(center=(screen_rect.centerx, screen_rect.centery - 50))
        subtitle_rect = self.subtitle_text.get_rect(center=(screen_rect.centerx, screen_rect.centery + 50))

        screen.blit(self.title_text, title_rect)
        screen.blit(self.subtitle_text, subtitle_rect)


class GameplayState(GameState):
    """Main gameplay state"""

    def __init__(self):
        # Create player at center of screen
        self.player = Player(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2)

        # Camera position (top-left corner of the view)
        self.camera_x = 0
        self.camera_y = 0

        # Create background dots surface
        # Make it 3x the screen size to allow for camera movement
        bg_width = WINDOW_WIDTH * 3
        bg_height = WINDOW_HEIGHT * 3
        self.background = pygame.Surface((bg_width, bg_height))
        self.background.fill(BLACK)

        # Draw dots on the background
        for x in range(0, bg_width, DOT_SPACING):
            for y in range(0, bg_height, DOT_SPACING):
                pygame.draw.circle(self.background, GRAY, (x, y), DOT_SIZE)

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                return "menu"
        return None

    def update(self, dt):
        # Update player
        self.player.update(dt)

        # Update camera position to follow player (with smoothing)
        target_camera_x = self.player.x - WINDOW_WIDTH // 2
        target_camera_y = self.player.y - WINDOW_HEIGHT // 2

        self.camera_x += (target_camera_x - self.camera_x) * CAMERA_LERP
        self.camera_y += (target_camera_y - self.camera_y) * CAMERA_LERP

    def render(self, screen):
        # Calculate camera offset for rendering
        camera_offset = (int(self.camera_x), int(self.camera_y))

        # Draw background with camera offset
        # We need to blit a portion of the background based on camera position
        screen.blit(self.background, (0, 0), 
                   (camera_offset[0], camera_offset[1], WINDOW_WIDTH, WINDOW_HEIGHT))

        # Draw player with camera offset
        self.player.render(screen, camera_offset)


class GameStateManager:
    """Game state manager"""

    def __init__(self):
        self.states = {
            "menu": MenuState(),
            "gameplay": GameplayState()
        }
        self.current_state = "menu"

    def handle_event(self, event):
        new_state = self.states[self.current_state].handle_event(event)
        if new_state and new_state in self.states:
            self.current_state = new_state

    def update(self, dt):
        self.states[self.current_state].update(dt)

    def render(self, screen):
        self.states[self.current_state].render(screen)
