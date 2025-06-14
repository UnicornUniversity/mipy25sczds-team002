import pygame
import math
from entities.entity import Entity
from utils.constants import GREEN, ENEMY_SIZE, ENEMY_SPEED

class Zombie(Entity):
    """Zombie entity that follows the player"""
    
    def __init__(self, x, y):
        """Initialize the zombie
        
        Args:
            x (float): Initial x position
            y (float): Initial y position
        """
        super().__init__(x, y, ENEMY_SIZE, ENEMY_SIZE, GREEN)
        self.speed = ENEMY_SPEED
    
    def update(self, dt, player_x, player_y):
        """Update zombie state to move towards player
        
        Args:
            dt (float): Time delta in seconds
            player_x (float): Player's x position
            player_y (float): Player's y position
        """
        # Calculate direction vector to player
        dx = player_x - self.x
        dy = player_y - self.y
        
        # Normalize the direction vector
        distance = math.sqrt(dx * dx + dy * dy)
        
        # Only move if not already at player position
        if distance > 0:
            dx /= distance
            dy /= distance
            
            # Move towards player
            self.x += dx * self.speed * dt
            self.y += dy * self.speed * dt
        
        # Call parent update to update rect
        super().update(dt)
    
    def render(self, screen, camera_offset=(0, 0)):
        """Render the zombie as a green circle
        
        Args:
            screen (pygame.Surface): Screen to render on
            camera_offset (tuple): Camera offset (x, y)
        """
        # Draw zombie as a circle instead of a rectangle
        center_x = self.rect.x + self.width // 2 - camera_offset[0]
        center_y = self.rect.y + self.height // 2 - camera_offset[1]
        pygame.draw.circle(screen, self.color, (center_x, center_y), self.width // 2)
