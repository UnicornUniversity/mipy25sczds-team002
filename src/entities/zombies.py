import pygame
import math
from entities.entity import Entity
from utils.constants import BLACK, ENEMY_SIZE, ENEMY_SPEED, OBJECT_SPEED_MULTIPLIER, TILE_OBJECT

class Zombie(Entity):
    """Zombie entity that follows the player"""

    def __init__(self, x, y):
        """Initialize the zombie

        Args:
            x (float): Initial x position
            y (float): Initial y position
        """
        super().__init__(x, y, ENEMY_SIZE, ENEMY_SIZE, BLACK)
        self.speed = ENEMY_SPEED
        self.is_on_object = False  # Flag to track if zombie is on an object
        self.map_generator = None  # Will be set by GameplayState

    def update(self, dt, player_x, player_y, map_generator=None):
        """Update zombie state to move towards player

        Args:
            dt (float): Time delta in seconds
            player_x (float): Player's x position
            player_y (float): Player's y position
            map_generator (MapGenerator, optional): Reference to the map generator
        """
        # Store map_generator reference if provided
        if map_generator:
            self.map_generator = map_generator

        # Calculate direction vector to player
        dx = player_x - self.x
        dy = player_y - self.y

        # Normalize the direction vector
        distance = math.sqrt(dx * dx + dy * dy)

        # Calculate base speed
        base_speed = self.speed

        # Check if zombie is on an object and apply speed multiplier if needed
        self.is_on_object = False
        if self.map_generator:
            tile_type = self.map_generator.get_tile_at(self.x + self.width // 2, self.y + self.height // 2)
            if tile_type == TILE_OBJECT:
                self.is_on_object = True
                base_speed *= OBJECT_SPEED_MULTIPLIER

        # Only move if not already at player position
        if distance > 0:
            dx /= distance
            dy /= distance

            # Move towards player with potentially reduced speed
            self.x += dx * base_speed * dt
            self.y += dy * base_speed * dt

        # Call parent update to update rect
        super().update(dt)

    def render(self, screen, camera_offset=(0, 0)):
        """Render the zombie as a black circle

        Args:
            screen (pygame.Surface): Screen to render on
            camera_offset (tuple): Camera offset (x, y)
        """
        # Calculate center position
        center_x = self.rect.x + self.width // 2 - camera_offset[0]
        center_y = self.rect.y + self.height // 2 - camera_offset[1]

        # Create a transparent surface for the zombie when on an object
        if self.is_on_object:
            # Create a surface with per-pixel alpha
            circle_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            # Draw a semi-transparent circle (128 is 50% opacity)
            pygame.draw.circle(circle_surface, (*self.color, 128), (self.width // 2, self.height // 2), self.width // 2)
            # Blit the surface to the screen
            screen.blit(circle_surface, (center_x - self.width // 2, center_y - self.height // 2))
        else:
            # Draw zombie normally when not on an object
            pygame.draw.circle(screen, self.color, (center_x, center_y), self.width // 2)