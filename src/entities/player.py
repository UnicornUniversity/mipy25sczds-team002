import pygame
import math
from entities.entity import Entity
from utils.constants import RED, PLAYER_SIZE, PLAYER_SPEED, TILE_SIZE, MAP_WIDTH, MAP_HEIGHT, OBJECT_SPEED_MULTIPLIER, TILE_OBJECT
from utils.sprite_loader import get_sprite

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
        self.debug_speed_multiplier = 1.0
        self.is_on_object = False  # Flag to track if player is on an object
        self.map_generator = None  # Will be set by GameplayState
        
        # Animation tracking for sprites
        self.animation_time = 0
        self.is_moving = False
        
        # Direction tracking for sprite flipping
        self.facing_left = False  # True if facing left, False if facing right

    def update(self, dt, map_generator=None):
        """Update player state based on input

        Args:
            dt (float): Time delta in seconds
            map_generator (MapGenerator, optional): Reference to the map generator
        """
        # Store map_generator reference if provided
        if map_generator:
            self.map_generator = map_generator

        # Get keyboard input
        keys = pygame.key.get_pressed()

        # Check for debug speed boost with Shift key
        if keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]:
            self.debug_speed_multiplier = 3.0  # 3x speed when Shift is pressed
        else:
            self.debug_speed_multiplier = 1.0

        # Calculate base speed with debug multiplier
        base_speed = self.speed * self.debug_speed_multiplier

        # Check if player is on an object and apply speed multiplier if needed
        self.is_on_object = False
        if self.map_generator:
            tile_type = self.map_generator.get_tile_at(self.x + self.width // 2, self.y + self.height // 2)
            if tile_type == TILE_OBJECT:
                self.is_on_object = True
                base_speed *= OBJECT_SPEED_MULTIPLIER

        # Store previous position for collision detection
        prev_x, prev_y = self.x, self.y
        
        # Reset movement flag
        self.is_moving = False

        # Move player based on arrow keys or WASD and track direction
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.x -= base_speed * dt
            self.is_moving = True
            self.facing_left = True  # Facing left
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.x += base_speed * dt
            self.is_moving = True
            self.facing_left = False  # Facing right
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.y -= base_speed * dt
            self.is_moving = True
            # Don't change horizontal facing for vertical movement
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.y += base_speed * dt
            self.is_moving = True
            # Don't change horizontal facing for vertical movement

        # Update animation time
        if self.is_moving:
            self.animation_time += dt
        else:
            self.animation_time = 0

        # Boundary checking to prevent player from leaving the map
        map_width_px = MAP_WIDTH * TILE_SIZE
        map_height_px = MAP_HEIGHT * TILE_SIZE

        # Keep player within map boundaries
        self.x = max(0, min(self.x, map_width_px - self.width))
        self.y = max(0, min(self.y, map_height_px - self.height))

        # Call parent update to update rect
        super().update(dt)

    def render(self, screen, camera_offset=(0, 0)):
        """Render the player using sprites with fallback

        Args:
            screen (pygame.Surface): Screen to render on
            camera_offset (tuple): Camera offset (x, y)
        """
        # Use only player_idle sprite for consistency - always the same character
        sprite = get_sprite('player_idle')
        
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
                    # Very subtle "bounce" effect during movement
                    bounce_offset = int(2 * abs(math.cos(self.animation_time * 8)))
                    sprite_y -= bounce_offset
                
                screen.blit(sprite, (sprite_x, sprite_y))
        else:
            # Fallback: draw circle if sprite not available
            center_x = screen_x + self.width // 2
            center_y = screen_y + self.height // 2

            if self.is_on_object:
                # Create a transparent surface for the player when on an object
                circle_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
                # Draw a semi-transparent circle (128 is 50% opacity)
                pygame.draw.circle(circle_surface, (*self.color, 128), (self.width // 2, self.height // 2), self.width // 2)
                # Blit the surface to the screen
                screen.blit(circle_surface, (center_x - self.width // 2, center_y - self.height // 2))
            else:
                # Draw player normally when not on an object
                pygame.draw.circle(screen, self.color, (center_x, center_y), self.width // 2)
