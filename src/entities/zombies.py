import pygame
import math
from entities.entity import Entity
from utils.constants import BLACK, ENEMY_SIZE, ENEMY_SPEED, OBJECT_SPEED_MULTIPLIER, TILE_OBJECT
from utils.sprite_loader import get_sprite

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
        
        # Animation tracking for sprites
        self.animation_time = 0
        self.is_moving = False
        
        # Direction tracking for sprite flipping
        self.facing_left = False  # True if facing left, False if facing right

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

        # Reset movement flag
        self.is_moving = False

        # Only move if not already at player position
        if distance > 5:  # Small threshold to prevent jittering
            dx /= distance
            dy /= distance

            # Move towards player with potentially reduced speed
            self.x += dx * base_speed * dt
            self.y += dy * base_speed * dt
            self.is_moving = True
            
            # Update facing direction based on horizontal movement
            if dx < -0.1:  # Moving left (with small threshold to avoid jittering)
                self.facing_left = True
            elif dx > 0.1:  # Moving right
                self.facing_left = False

        # Update animation time
        if self.is_moving:
            self.animation_time += dt
        else:
            self.animation_time = 0

        # Call parent update to update rect
        super().update(dt)

    def render(self, screen, camera_offset=(0, 0)):
        """Render the zombie using sprites with fallback

        Args:
            screen (pygame.Surface): Screen to render on
            camera_offset (tuple): Camera offset (x, y)
        """
        # Use only zombie_basic_1 sprite for consistency - always the same zombie
        sprite = get_sprite('zombie_basic_1')
        
        # Calculate screen position
        screen_x = self.rect.x - camera_offset[0]
        screen_y = self.rect.y - camera_offset[1]
        
        if sprite:
            # Flip sprite horizontally if facing left
            if self.facing_left:
                sprite = pygame.transform.flip(sprite, True, False)  # Flip horizontally
            
            # Center the sprite on the entity position
            sprite_x = screen_x - (sprite.get_width() - self.width) // 2
            sprite_y = screen_y - (sprite.get_height() - self.height) // 2
            
            # Apply transparency if on object
            if self.is_on_object:
                # Create a copy with alpha for transparency effect
                sprite_copy = sprite.copy()
                sprite_copy.set_alpha(180)  # Semi-transparent
                screen.blit(sprite_copy, (sprite_x, sprite_y))
            else:
                # Optional: slight visual feedback for movement
                if self.is_moving:
                    # Very subtle "wobble" effect during movement (slower than player)
                    wobble_offset = int(1 * abs(math.sin(self.animation_time * 4)))
                    sprite_x += wobble_offset
                
                screen.blit(sprite, (sprite_x, sprite_y))
        else:
            # Fallback: draw circle if sprite not available
            center_x = screen_x + self.width // 2
            center_y = screen_y + self.height // 2

            if self.is_on_object:
                # Create a transparent surface for the zombie when on an object
                circle_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
                # Draw a semi-transparent circle (128 is 50% opacity)
                pygame.draw.circle(circle_surface, (*self.color, 128), (self.width // 2, self.height // 2), self.width // 2)
                # Blit the surface to the screen
                screen.blit(circle_surface, (center_x - self.width // 2, center_y - self.height // 2))
            else:
                # Draw zombie normally when not on an object
                pygame.draw.circle(screen, self.color, (center_x, center_y), self.width // 2)