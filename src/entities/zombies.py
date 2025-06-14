import pygame
import math
from entities.entity import Entity
from utils.constants import (
    BLACK, ENEMY_SIZE, ENEMY_SPEED, OBJECT_SPEED_MULTIPLIER, TILE_OBJECT,
    ZOMBIE_HEALTH, ZOMBIE_DAMAGE, ZOMBIE_ATTACK_COOLDOWN,
    TOUGH_ZOMBIE_HEALTH, TOUGH_ZOMBIE_DAMAGE, TOUGH_ZOMBIE_SPEED,
    ZOMBIE_ATTACK_RANGE, ZOMBIE_ATTACK_DURATION, ZOMBIE_ATTACK_KNOCKBACK,
    RED
)
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
        self.health = ZOMBIE_HEALTH
        self.attack_timer = 0  # Timer for attack cooldown
        self.is_attacking = False  # Flag for attack animation
        self.attack_animation_timer = 0  # Timer for attack animation
        
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

        # Update attack timer
        if self.attack_timer > 0:
            self.attack_timer -= dt

        # Update attack animation
        if self.is_attacking:
            self.attack_animation_timer -= dt
            if self.attack_animation_timer <= 0:
                self.is_attacking = False

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

        # Only move if not already at player position and not attacking
        if distance > 5 and not self.is_attacking:  # Small threshold to prevent jittering
            dx /= distance
            dy /= distance

            # Store previous position for collision response
            prev_x, prev_y = self.x, self.y

            # Try to move in x direction
            new_x = self.x + dx * base_speed * dt
            if self.map_generator and not self.map_generator.is_walkable(new_x + self.width // 2, self.y + self.height // 2):
                # If x movement would cause collision, try to slide along the wall
                if self.map_generator.is_walkable(self.x + self.width // 2, new_x + self.height // 2):
                    self.y += dy * base_speed * dt
            else:
                self.x = new_x

            # Try to move in y direction
            new_y = self.y + dy * base_speed * dt
            if self.map_generator and not self.map_generator.is_walkable(self.x + self.width // 2, new_y + self.height // 2):
                # If y movement would cause collision, try to slide along the wall
                if self.map_generator.is_walkable(new_x + self.width // 2, self.y + self.height // 2):
                    self.x += dx * base_speed * dt
            else:
                self.y = new_y

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

    def attack(self, player):
        """Attack the player if cooldown has expired

        Args:
            player: The player to attack

        Returns:
            bool: True if attack was successful, False otherwise
        """
        if self.attack_timer <= 0:
            # Calculate distance to player
            dx = player.x - self.x
            dy = player.y - self.y
            distance = math.sqrt(dx * dx + dy * dy)

            # Only attack if within range
            if distance <= ZOMBIE_ATTACK_RANGE:
                # Start attack animation
                self.is_attacking = True
                self.attack_animation_timer = ZOMBIE_ATTACK_DURATION

                # Reset attack timer
                self.attack_timer = ZOMBIE_ATTACK_COOLDOWN

                # Deal damage to player
                if player.take_damage(ZOMBIE_DAMAGE):
                    # Apply knockback to player
                    if distance > 0:  # Avoid division by zero
                        knockback_x = dx / distance * ZOMBIE_ATTACK_KNOCKBACK
                        knockback_y = dy / distance * ZOMBIE_ATTACK_KNOCKBACK
                        player.x += knockback_x
                        player.y += knockback_y
                    return True

        return False

    def take_damage(self, amount):
        """Reduce zombie health by the specified amount

        Args:
            amount (int): Amount of damage to take

        Returns:
            bool: True if zombie died, False otherwise
        """
        self.health -= amount
        if self.health <= 0:
            self.health = 0
            return True  # Zombie died
        return False

    def is_dead(self):
        """Check if the zombie is dead

        Returns:
            bool: True if zombie health is 0, False otherwise
        """
        return self.health <= 0

    def render(self, screen, camera_offset=(0, 0)):
        """Render the zombie using sprites with fallback

        Args:
            screen (pygame.Surface): Screen to render on
            camera_offset (tuple): Camera offset (x, y)
        """
        # Calculate screen position
        screen_x = self.rect.x - camera_offset[0]
        screen_y = self.rect.y - camera_offset[1]
        
        # Calculate center position (needed for both sprite and fallback rendering)
        center_x = screen_x + self.width // 2
        center_y = screen_y + self.height // 2

        # Use only zombie_basic_1 sprite for consistency - always the same zombie
        sprite = get_sprite('zombie_basic_1')

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

                # Add attack animation
                if self.is_attacking:
                    # Scale up slightly during attack
                    scale = 1.2
                    scaled_sprite = pygame.transform.scale(sprite, 
                        (int(sprite.get_width() * scale), int(sprite.get_height() * scale)))
                    # Center the scaled sprite
                    sprite_x -= (scaled_sprite.get_width() - sprite.get_width()) // 2
                    sprite_y -= (scaled_sprite.get_height() - sprite.get_height()) // 2
                    screen.blit(scaled_sprite, (sprite_x, sprite_y))
                else:
                    screen.blit(sprite, (sprite_x, sprite_y))
        else:
            # Fallback: draw circle if sprite not available
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


class ToughZombie(Zombie):
    """Tougher zombie entity that follows the player but is slower"""

    def __init__(self, x, y):
        """Initialize the tough zombie

        Args:
            x (float): Initial x position
            y (float): Initial y position
        """
        # Call parent constructor
        super().__init__(x, y)

        # Override properties for tough zombie
        self.color = RED
        self.speed = TOUGH_ZOMBIE_SPEED
        self.health = TOUGH_ZOMBIE_HEALTH

    def attack(self, player):
        """Attack the player if cooldown has expired

        Args:
            player: The player to attack

        Returns:
            bool: True if attack was successful, False otherwise
        """
        if self.attack_timer <= 0:
            # Reset attack timer
            self.attack_timer = ZOMBIE_ATTACK_COOLDOWN

            # Deal damage to player (more damage than regular zombie)
            return player.take_damage(TOUGH_ZOMBIE_DAMAGE)

        return False
