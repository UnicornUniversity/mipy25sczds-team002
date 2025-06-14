import pygame
import math
from entities.entity import Entity
from systems.weapons import Pistol
from utils.constants import RED, PLAYER_SIZE, PLAYER_SPEED, TILE_SIZE, MAP_WIDTH, MAP_HEIGHT, OBJECT_SPEED_MULTIPLIER, TILE_OBJECT, PLAYER_MAX_HEALTH
from utils.sprite_loader import get_sprite, get_texture
from systems import collisions


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
        self.health = PLAYER_MAX_HEALTH
        self.is_invulnerable = False  # Flag for temporary invulnerability after taking damage
        self.invulnerability_timer = 0  # Timer for invulnerability

        # Weapon handling
        self.weapon = Pistol()  # Start with a pistol
        self.aim_angle = 0  # Angle in radians (0 = right, pi/2 = down)

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

        # Update invulnerability timer if player is invulnerable
        if self.is_invulnerable:
            self.invulnerability_timer -= dt
            if self.invulnerability_timer <= 0:
                self.is_invulnerable = False
                self.invulnerability_timer = 0

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

        # Calculate movement direction based on arrow keys or WASD
        dx = 0
        dy = 0

        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            dx -= 1
            self.facing_left = True  # Facing left
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            dx += 1
            self.facing_left = False  # Facing right
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            dy -= 1
            # Don't change horizontal facing for vertical movement
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            dy += 1
            # Don't change horizontal facing for vertical movement

        # Use the collision system to resolve movement with wall collision detection
        if dx != 0 or dy != 0:
            self.is_moving = True
            new_x, new_y, collided = collisions.resolve_movement(self, dx, dy, dt, base_speed)
            self.x, self.y = new_x, new_y
        else:
            self.is_moving = False

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

        # Update weapon
        if self.weapon:
            self.weapon.update(dt)

            # Handle reload with R key
            if keys[pygame.K_r]:
                self.weapon.reload()

        # Call parent update to update rect
        super().update(dt)

    def take_damage(self, amount):
        """Reduce player health by the specified amount if not invulnerable

        Args:
            amount (int): Amount of damage to take

        Returns:
            bool: True if damage was taken, False if invulnerable
        """
        if self.is_invulnerable:
            return False

        self.health -= amount
        if self.health < 0:
            self.health = 0

        # Make player invulnerable for a short time after taking damage
        self.is_invulnerable = True
        self.invulnerability_timer = 0.5  # Half a second of invulnerability

        return True

    def is_dead(self):
        """Check if the player is dead

        Returns:
            bool: True if player health is 0, False otherwise
        """
        return self.health <= 0

    def update_aim(self, mouse_pos, camera_offset):
        """Update the aim angle based on mouse position

        Args:
            mouse_pos (tuple): Mouse position (x, y)
            camera_offset (tuple): Camera offset (x, y)
        """
        # Calculate player center in screen coordinates
        player_center_x = self.rect.x + self.width // 2 - camera_offset[0]
        player_center_y = self.rect.y + self.height // 2 - camera_offset[1]

        # Calculate vector from player to mouse
        dx = mouse_pos[0] - player_center_x
        dy = mouse_pos[1] - player_center_y

        # Calculate angle (atan2 returns angle in radians)
        self.aim_angle = math.atan2(dy, dx)

    def shoot(self):
        """Attempt to shoot a bullet

        Returns:
            Bullet or None: A new bullet if shot was successful, None otherwise
        """
        if self.weapon:
            # Auto-reload if magazine is empty and not already reloading
            if self.weapon.ammo <= 0 and not self.weapon.is_reloading:
                self.weapon.reload()

            if self.weapon.can_shoot():
                # Calculate bullet spawn position (slightly in front of player in aim direction)
                spawn_distance = self.width // 2 + 5  # 5 pixels in front of player edge
                spawn_x = self.x + self.width // 2 + math.cos(self.aim_angle) * spawn_distance
                spawn_y = self.y + self.height // 2 + math.sin(self.aim_angle) * spawn_distance

                # Shoot the weapon
                return self.weapon.shoot(spawn_x, spawn_y, self.aim_angle)

        return None

    def render(self, screen, camera_offset=(0, 0)):
        """Render the player with a sprite that rotates based on weapon aim direction

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

        # Get player weapon sprite that rotates with aim
        # Use reload sprite if player is reloading
        if self.weapon and self.weapon.is_reloading:
            weapon_sprite = get_texture('survivor', 'survivor1_reload')
        else:
            weapon_sprite = get_texture('survivor', 'survivor1_machine')

        # We'll use the weapon sprite as the main player sprite
        if weapon_sprite:
                # Convert aim angle from radians to degrees for rotation
                # Subtract 180 degrees (90 for default orientation + 90 for left rotation)
                rotation_angle = math.degrees(-self.aim_angle)

                # Rotate the weapon sprite
                rotated_weapon = pygame.transform.rotate(weapon_sprite, rotation_angle)

                # Calculate position to center the rotated weapon on the player
                weapon_x = center_x - rotated_weapon.get_width() // 2
                weapon_y = center_y - rotated_weapon.get_height() // 2

                # Apply transparency if on object
                if self.is_on_object:
                    rotated_weapon.set_alpha(180)  # Semi-transparent

                # Draw the rotated weapon sprite
                screen.blit(rotated_weapon, (weapon_x, weapon_y))
        else:
            # Fallback: draw circle if sprite not available
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

                # Draw aim direction line as fallback
                line_length = self.width  # Length of the aim line
                end_x = center_x + math.cos(self.aim_angle) * line_length
                end_y = center_y + math.sin(self.aim_angle) * line_length
                pygame.draw.line(screen, (0, 0, 0), (center_x, center_y), (end_x, end_y), 2)
