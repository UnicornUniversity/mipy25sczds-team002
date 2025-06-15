import pygame
import math
from entities.entity import Entity
from systems.weapons import Pistol, Shotgun, AssaultRifle, SniperRifle, Bazooka
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

        # Weapon inventory (slots 1-5)
        self.weapons = [None] * 5  # Initialize with 5 empty slots
        self.weapons[0] = Pistol()  # Start with a pistol in slot 1
        self.current_weapon_slot = 0  # Current active weapon slot (0-4)
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

        # Update current weapon
        current_weapon = self.get_current_weapon()
        if current_weapon:
            current_weapon.update(dt)

            # Handle reload with R key
            if keys[pygame.K_r]:
                current_weapon.reload()

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

    def get_current_weapon(self):
        """Get the current weapon from the inventory

        Returns:
            Weapon or None: The current weapon, or None if no weapon in the current slot
        """
        if 0 <= self.current_weapon_slot < len(self.weapons):
            return self.weapons[self.current_weapon_slot]
        return None

    def switch_weapon(self, slot):
        """Switch to a weapon in the specified slot

        Args:
            slot (int): The slot to switch to (0-4)

        Returns:
            bool: True if successfully switched, False if the slot is empty or invalid
        """
        if 0 <= slot < len(self.weapons) and self.weapons[slot] is not None:
            self.current_weapon_slot = slot
            return True
        return False

    def add_weapon(self, weapon, auto_switch=True):
        """Add a weapon to the inventory

        Args:
            weapon: The weapon to add
            auto_switch (bool): Whether to automatically switch to the new weapon if it's better

        Returns:
            bool: True if successfully added, False if inventory is full
        """
        # Find the first empty slot
        for i in range(len(self.weapons)):
            if self.weapons[i] is None:
                self.weapons[i] = weapon

                # Auto-switch to the new weapon if it's better than the current one
                if auto_switch:
                    current_weapon = self.get_current_weapon()
                    if current_weapon is None:
                        self.current_weapon_slot = i
                    else:
                        # Compare weapon types using the hierarchy
                        from entities.items import Weapon
                        current_type = None
                        new_type = None

                        # Determine current weapon type
                        for weapon_type in Weapon.WEAPON_HIERARCHY:
                            if weapon_type in current_weapon.name.lower():
                                current_type = weapon_type
                                break

                        # Determine new weapon type
                        for weapon_type in Weapon.WEAPON_HIERARCHY:
                            if weapon_type in weapon.name.lower():
                                new_type = weapon_type
                                break

                        # Switch if new weapon is better
                        if current_type and new_type:
                            current_index = Weapon.WEAPON_HIERARCHY.index(current_type)
                            new_index = Weapon.WEAPON_HIERARCHY.index(new_type)
                            if new_index > current_index:
                                self.current_weapon_slot = i

                return True

        return False

    def shoot(self):
        """Attempt to shoot a bullet

        Returns:
            Bullet or None: A new bullet if shot was successful, None otherwise
        """
        current_weapon = self.get_current_weapon()
        if current_weapon:
            # Auto-reload if magazine is empty and not already reloading
            if current_weapon.ammo <= 0 and not current_weapon.is_reloading:
                current_weapon.reload()

            if current_weapon.can_shoot():
                # Calculate bullet spawn position (slightly in front of player in aim direction)
                spawn_distance = self.width // 2 + 5  # 5 pixels in front of player edge
                spawn_x = self.x + self.width // 2 + math.cos(self.aim_angle) * spawn_distance
                spawn_y = self.y + self.height // 2 + math.sin(self.aim_angle) * spawn_distance

                # Shoot the weapon
                return current_weapon.shoot(spawn_x, spawn_y, self.aim_angle)

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

        # Get current weapon
        current_weapon = self.get_current_weapon()

        # Get player weapon sprite that rotates with aim
        # Use reload sprite if player is reloading
        if current_weapon and current_weapon.is_reloading:
            weapon_sprite = get_texture('survivor', 'survivor1_reload')
        else:
            weapon_sprite = get_texture('survivor', 'survivor1_machine')

        # We'll use the weapon sprite as the main player sprite
        if weapon_sprite:
                # Convert aim angle from radians to degrees for rotation
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

                # Draw weapon inventory UI
                self._render_weapon_inventory(screen)
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

    def _render_weapon_inventory(self, screen):
        """Render the weapon inventory UI

        Args:
            screen (pygame.Surface): Screen to render on
        """
        # Create a font for the weapon names
        font = pygame.font.Font(None, 24)

        # Define the position and size of the inventory UI
        ui_x = 10
        ui_y = screen.get_height() - 40
        slot_width = 100
        slot_height = 30
        padding = 5

        # Draw each weapon slot
        for i in range(len(self.weapons)):
            # Calculate slot position
            slot_x = ui_x + i * (slot_width + padding)
            slot_y = ui_y

            # Draw slot background (highlight current slot)
            if i == self.current_weapon_slot:
                slot_color = (200, 200, 0)  # Yellow for current slot
            else:
                slot_color = (100, 100, 100)  # Gray for other slots

            # Draw slot rectangle
            pygame.draw.rect(screen, slot_color, (slot_x, slot_y, slot_width, slot_height))
            pygame.draw.rect(screen, (0, 0, 0), (slot_x, slot_y, slot_width, slot_height), 2)  # Black border

            # Draw weapon name if slot is not empty
            if self.weapons[i] is not None:
                # Get weapon name
                weapon_name = self.weapons[i].name

                # Render weapon name
                text = font.render(f"{i+1}: {weapon_name}", True, (0, 0, 0))

                # Center text in slot
                text_x = slot_x + (slot_width - text.get_width()) // 2
                text_y = slot_y + (slot_height - text.get_height()) // 2

                # Draw text
                screen.blit(text, (text_x, text_y))
            else:
                # Draw empty slot text
                text = font.render(f"{i+1}: Empty", True, (0, 0, 0))

                # Center text in slot
                text_x = slot_x + (slot_width - text.get_width()) // 2
                text_y = slot_y + (slot_height - text.get_height()) // 2

                # Draw text
                screen.blit(text, (text_x, text_y))
