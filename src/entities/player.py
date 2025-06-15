import pygame
import math
from entities.entity import Entity
from utils.constants import (
    PLAYER_SIZE, PLAYER_SPEED, PLAYER_MAX_HEALTH, WHITE, MAP_WIDTH, MAP_HEIGHT, TILE_SIZE,
    OBJECT_SPEED_MULTIPLIER, TILE_OBJECT
)
from systems.collisions import resolve_movement


class Player(Entity):
    """Player entity s weapon inventory systémem"""

    def __init__(self, x, y):
        """Initialize the player"""
        super().__init__(x, y, PLAYER_SIZE, PLAYER_SIZE, WHITE)

        # Health system
        self.health = PLAYER_MAX_HEALTH
        self.max_health = PLAYER_MAX_HEALTH

        # Movement
        self.speed = PLAYER_SPEED
        self.aim_angle = 0
        self.map_generator = None  # Will be set by game state

        # === WEAPON INVENTORY SYSTEM ===
        from systems.weapons import WeaponInventory, WeaponFactory
        self.weapon_inventory = WeaponInventory(max_weapons=5)

        # Start with pistol
        starting_weapon = WeaponFactory.create_weapon("pistol")
        self.weapon_inventory.add_weapon(starting_weapon, auto_switch=True)

        # Sprite system
        self.current_sprite = None
        self.sprite_state = "stand"  # stand, gun, reload, etc.
        self._load_sprites()

    def _load_sprites(self):
        """Load player sprites from survivor category"""
        from utils.sprite_loader import get_texture
        self.sprites = {}

        # Load all survivor sprites
        sprite_mappings = {
            'stand': 'survivor1_stand',
            'gun': 'survivor1_gun',
            'hold': 'survivor1_hold',
            'machine': 'survivor1_machine',
            'reload': 'survivor1_reload',
            'silencer': 'survivor1_silencer'
        }

        for state, sprite_name in sprite_mappings.items():
            sprite = get_texture("survivor", sprite_name)
            if sprite:
                # Use original sprite size to match zombie size
                self.sprites[state] = sprite
            else:
                print(f"Warning: Could not load survivor sprite: {sprite_name}")

        # Set initial sprite
        self.current_sprite = self.sprites.get('stand')

    def _update_sprite_state(self):
        """Update sprite based on current weapon and action"""
        current_weapon = self.weapon_inventory.get_current_weapon()

        if current_weapon and current_weapon.is_reloading:
            self.sprite_state = "reload"
        elif current_weapon:
            # Choose sprite based on weapon type
            weapon_name = current_weapon.name.lower()
            if weapon_name == "pistol":
                self.sprite_state = "gun"
            elif weapon_name in ["shotgun", "assault_rifle", "sniper_rifle"]:
                self.sprite_state = "machine"
            elif weapon_name == "bazooka":
                self.sprite_state = "hold"
            else:
                self.sprite_state = "gun"
        else:
            self.sprite_state = "stand"

        # Update current sprite
        self.current_sprite = self.sprites.get(self.sprite_state, self.sprites.get('stand'))

    def set_map_generator(self, map_generator):
        """Set map generator reference for collision detection"""
        self.map_generator = map_generator

    def update(self, dt, map_generator=None):
        """Update player state"""
        if map_generator:
            self.map_generator = map_generator

        # Get current key states from pygame
        keys_pressed = pygame.key.get_pressed()
        self._handle_movement(dt, keys_pressed)

        # Update current weapon
        current_weapon = self.weapon_inventory.get_current_weapon()
        if current_weapon:
            current_weapon.update(dt)

        # Update sprite state
        self._update_sprite_state()

        super().update(dt)

    def render(self, screen, camera_offset=(0, 0)):
        """Render the player with sprite"""
        # Calculate screen position
        draw_x = self.rect.x - camera_offset[0]
        draw_y = self.rect.y - camera_offset[1]

        if self.current_sprite:
            # Calculate rotation based on aim angle
            rotation_angle = math.degrees(-self.aim_angle)
            rotated_sprite = pygame.transform.rotate(self.current_sprite, rotation_angle)

            # Center the sprite on the entity
            sprite_rect = rotated_sprite.get_rect()
            sprite_x = draw_x + (self.width - sprite_rect.width) // 2
            sprite_y = draw_y + (self.height - sprite_rect.height) // 2
            screen.blit(rotated_sprite, (sprite_x, sprite_y))
        else:
            # Fallback to rectangle rendering
            pygame.draw.rect(screen, self.color, (draw_x, draw_y, self.width, self.height))

    def shoot(self):
        """Shoot with current weapon"""
        current_weapon = self.weapon_inventory.get_current_weapon()
        if current_weapon and current_weapon.can_shoot():
            # Pass player center position to weapon
            player_center_x = self.x + self.width / 2
            player_center_y = self.y + self.height / 2
            return current_weapon.shoot(player_center_x, player_center_y, self.aim_angle)
        return None

    def reload(self):
        """Reload current weapon"""
        current_weapon = self.weapon_inventory.get_current_weapon()
        if current_weapon:
            current_weapon.reload()

    def switch_weapon(self, slot):
        """Switch to weapon in specified slot"""
        return self.weapon_inventory.switch_weapon(slot)

    def add_weapon(self, weapon, auto_switch=True):
        """Add weapon to inventory"""
        return self.weapon_inventory.add_weapon(weapon, auto_switch)

    def get_current_weapon(self):
        """Get currently equipped weapon"""
        return self.weapon_inventory.get_current_weapon()

    def cycle_weapons_forward(self):
        """Cycle to next weapon"""
        return self.weapon_inventory.cycle_weapon_forward()

    def cycle_weapons_backward(self):
        """Cycle to previous weapon"""
        return self.weapon_inventory.cycle_weapon_backward()

    def get_weapon_info(self):
        """Get current weapon info for UI"""
        current_weapon = self.weapon_inventory.get_current_weapon()
        if current_weapon:
            return {
                'name': current_weapon.name,
                'ammo': current_weapon.ammo,
                'magazine_size': current_weapon.magazine_size,
                'is_reloading': current_weapon.is_reloading,
                'reload_progress': 1.0 - (
                        current_weapon.reload_timer / current_weapon.reload_time) if current_weapon.is_reloading else 1.0
            }
        return None

    def get_inventory_status(self):
        """Get full inventory status for UI"""
        return self.weapon_inventory.get_inventory_status()

    def update_aim(self, mouse_pos, camera_offset):
        """Update aiming direction"""
        # Calculate player center in screen coordinates
        player_screen_x = self.rect.centerx - camera_offset[0]
        player_screen_y = self.rect.centery - camera_offset[1]

        # Calculate angle to mouse
        dx = mouse_pos[0] - player_screen_x
        dy = mouse_pos[1] - player_screen_y
        self.aim_angle = math.atan2(dy, dx)

    def take_damage(self, damage):
        """Take damage"""
        self.health = max(0, self.health - damage)
        return self.health > 0

    def heal(self, amount):
        """Heal player"""
        self.health = min(self.max_health, self.health + amount)

    def is_alive(self):
        """Check if player is alive"""
        return self.health > 0

    def is_dead(self):
        """Check if player is dead"""
        return self.health <= 0

    def _handle_movement(self, dt, keys_pressed):
        """Handle player movement based on input with collision detection"""
        dx = dy = 0

        if keys_pressed[pygame.K_a] or keys_pressed[pygame.K_LEFT]:
            dx = -1
        if keys_pressed[pygame.K_d] or keys_pressed[pygame.K_RIGHT]:
            dx = 1
        if keys_pressed[pygame.K_w] or keys_pressed[pygame.K_UP]:
            dy = -1
        if keys_pressed[pygame.K_s] or keys_pressed[pygame.K_DOWN]:
            dy = 1

        # Only process movement if there's input
        if dx != 0 or dy != 0:
            # Normalize diagonal movement
            if dx != 0 and dy != 0:
                length = math.sqrt(dx * dx + dy * dy)
                dx /= length
                dy /= length

            # Calculate base speed
            base_speed = self.speed

            # Check if player is on an object and apply speed multiplier if needed
            if self.map_generator:
                tile_type = self.map_generator.get_tile_at(self.x + self.width // 2, self.y + self.height // 2)
                if tile_type == TILE_OBJECT:
                    base_speed *= OBJECT_SPEED_MULTIPLIER

            # Use collision system to resolve movement
            new_x, new_y, collided = resolve_movement(self, dx, dy, dt, base_speed)

            # Check map boundaries
            map_width_px = MAP_WIDTH * TILE_SIZE
            map_height_px = MAP_HEIGHT * TILE_SIZE

            # Clamp to map boundaries
            new_x = max(0, min(new_x, map_width_px - self.width))
            new_y = max(0, min(new_y, map_height_px - self.height))

            # Apply the movement
            self.x = new_x
            self.y = new_y
