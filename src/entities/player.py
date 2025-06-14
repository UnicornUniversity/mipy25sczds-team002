import pygame
from entities.entity import Entity
from utils.constants import RED, PLAYER_SIZE, PLAYER_SPEED

class Player(Entity):
    """Player entity controlled by the user"""
    
    def __init__(self, x, y):
        """Initialize the player
        
        Args:
            x (float): Initial x position
            y (float): Initial y position
        """
        super().__init__(x, y, PLAYER_SIZE, PLAYER_SIZE, RED)
        self.speed = PLAYER_SPEED
    
    def update(self, dt):
        """Update player state based on input
        
        Args:
            dt (float): Time delta in seconds
        """
        # Get keyboard input
        keys = pygame.key.get_pressed()
        
        # Move player based on arrow keys or WASD
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.x -= self.speed * dt
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.x += self.speed * dt
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.y -= self.speed * dt
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.y += self.speed * dt
        
        # Call parent update to update rect
        super().update(dt)
    
    def render(self, screen, camera_offset=(0, 0)):
        """Render the player as a circle
        
        Args:
            screen (pygame.Surface): Screen to render on
            camera_offset (tuple): Camera offset (x, y)
        """
        # Draw player as a circle instead of a rectangle
        center_x = self.rect.x + self.width // 2 - camera_offset[0]
        center_y = self.rect.y + self.height // 2 - camera_offset[1]
        pygame.draw.circle(screen, self.color, (center_x, center_y), self.width // 2)
