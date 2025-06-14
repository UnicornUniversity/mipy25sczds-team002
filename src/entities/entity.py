import pygame
from utils.constants import BLACK

class Entity:
    """Base class for all game entities"""
    
    def __init__(self, x, y, width, height, color=BLACK):
        """Initialize the entity
        
        Args:
            x (float): Initial x position
            y (float): Initial y position
            width (int): Entity width
            height (int): Entity height
            color (tuple): RGB color tuple
        """
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color = color
        self.rect = pygame.Rect(x, y, width, height)
    
    def update(self, dt):
        """Update entity state
        
        Args:
            dt (float): Time delta in seconds
        """
        # Update the rect position to match the entity position
        self.rect.x = int(self.x)
        self.rect.y = int(self.y)
    
    def render(self, screen, camera_offset=(0, 0)):
        """Render the entity
        
        Args:
            screen (pygame.Surface): Screen to render on
            camera_offset (tuple): Camera offset (x, y)
        """
        # Draw the entity with camera offset
        draw_x = self.rect.x - camera_offset[0]
        draw_y = self.rect.y - camera_offset[1]
        pygame.draw.rect(screen, self.color, (draw_x, draw_y, self.width, self.height))