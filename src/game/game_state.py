import pygame


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
        self.title_text = self.font.render("MIPY GAME", True, (255, 255, 255))
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
        self.player_x = 400
        self.player_y = 300

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                return "menu"
        return None

    def update(self, dt):
        keys = pygame.key.get_pressed()
        speed = 200  # pixelů za sekundu

        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.player_x -= speed * dt
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.player_x += speed * dt
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.player_y -= speed * dt
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.player_y += speed * dt

    def render(self, screen):
        # Draw player as a red square
        pygame.draw.rect(screen, (255, 0, 0), (self.player_x, self.player_y, 32, 32))


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