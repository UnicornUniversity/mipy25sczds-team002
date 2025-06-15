"""
Item Spawner - Manages spawning of all items including powerups
"""

import random
import math
from utils.constants import (
    MAP_WIDTH, MAP_HEIGHT, TILE_SIZE, TILE_GRASS, TILE_OBJECT
)
from systems.items import ItemFactory, create_random_item, create_random_powerup


class ItemSpawner:
    """Manages spawning of items across the map"""

    def __init__(self, map_generator):
        """Initialize item spawner

        Args:
            map_generator: Reference to the map generator for tile checking
        """
        self.map_generator = map_generator
        self.items = []
        self.max_items = 20  # Maximum items on map at once
        self.spawn_timer = 0
        self.spawn_interval = 8.0  # Spawn item every 8 seconds
        self.powerup_spawn_timer = 0
        self.powerup_spawn_interval = 25.0  # Spawn powerup every 25 seconds
        self.ui = None  # UI reference for notifications, set by game state

    def _is_item_expired(self, item):
        """Check if item is expired, handling both method and attribute cases

        Args:
            item: Item to check

        Returns:
            bool: True if item is expired
        """
        is_expired_attr = getattr(item, 'is_expired', None)
        if callable(is_expired_attr):
            return is_expired_attr()
        elif isinstance(is_expired_attr, bool):
            return is_expired_attr
        else:
            # Default to not expired if attribute doesn't exist
            return False

    def _try_pickup_item(self, item, player):
        """Try to pickup item using available methods

        Args:
            item: Item to pickup
            player: Player instance

        Returns:
            bool: True if item was picked up successfully
        """
        # Try 'pickup' method first (if exists)
        if hasattr(item, 'pickup') and callable(item.pickup):
            return item.pickup(player)
        # Try 'collect' method as fallback
        elif hasattr(item, 'collect') and callable(item.collect):
            return item.collect(player)
        else:
            # No pickup method available
            return False

    def update(self, dt):
        """Update spawner timers and spawn items

        Args:
            dt (float): Time delta in seconds
        """
        # Update all items
        expired_items = []
        for item in self.items:
            if hasattr(item, 'update'):
                item.update(dt)
            if self._is_item_expired(item):
                expired_items.append(item)

        # Remove expired items
        for item in expired_items:
            self.items.remove(item)

        # Update spawn timers
        self.spawn_timer += dt
        self.powerup_spawn_timer += dt

        # Spawn basic items
        if self.spawn_timer >= self.spawn_interval and len(self.items) < self.max_items:
            self.spawn_random_item()
            self.spawn_timer = 0

        # Spawn powerups (less frequent)
        if self.powerup_spawn_timer >= self.powerup_spawn_interval:
            self.spawn_powerup()
            self.powerup_spawn_timer = 0

    def spawn_random_item(self, position=None, near_player=False, player_pos=None):
        """Spawn a random basic item

        Args:
            position (tuple, optional): Specific (x, y) position to spawn at
            near_player (bool): Whether to spawn near the player
            player_pos (tuple, optional): Player position (x, y) if near_player is True

        Returns:
            Item: The spawned item, or None if no suitable position was found
        """
        spawn_pos = position or self._find_spawn_position(near_player, player_pos)
        if spawn_pos:
            # Create random basic item (health, ammo, weapon)
            item = create_random_item(spawn_pos[0], spawn_pos[1], powerup_chance=0.0)
            if item:
                self.items.append(item)
                return item
        return None

    def spawn_powerup(self, position=None, near_player=False, player_pos=None):
        """Spawn a powerup

        Args:
            position (tuple, optional): Specific (x, y) position to spawn at
            near_player (bool): Whether to spawn near the player
            player_pos (tuple, optional): Player position (x, y) if near_player is True

        Returns:
            Powerup: The spawned powerup, or None if no suitable position was found
        """
        spawn_pos = position or self._find_spawn_position(near_player, player_pos)
        if spawn_pos:
            powerup = create_random_powerup(spawn_pos[0], spawn_pos[1])
            if powerup:
                self.items.append(powerup)
                print(f"Powerup spawned: {powerup.item_type}")
                return powerup
        return None

    def spawn_specific_item(self, item_type, position=None, near_player=False, player_pos=None, **kwargs):
        """Spawn a specific item type

        Args:
            item_type (str): Type of item to spawn
            position (tuple, optional): Specific (x, y) position
            near_player (bool): Whether to spawn near player
            player_pos (tuple, optional): Player position if near_player is True
            **kwargs: Additional arguments for item creation

        Returns:
            Item: The spawned item, or None if failed
        """
        spawn_pos = position or self._find_spawn_position(near_player, player_pos)
        if spawn_pos:
            item = ItemFactory.create_item(item_type, spawn_pos[0], spawn_pos[1], **kwargs)
            if item:
                self.items.append(item)
                return item
        return None

    def spawn_weapon(self, weapon_type, position=None, near_player=False, player_pos=None):
        """Spawn a specific weapon

        Args:
            weapon_type (str): Type of weapon to spawn
            position (tuple, optional): Specific (x, y) position
            near_player (bool): Whether to spawn near player
            player_pos (tuple, optional): Player position if near_player is True

        Returns:
            WeaponPickup: The spawned weapon, or None if failed
        """
        return self.spawn_specific_item("weapon", position, near_player, player_pos, weapon_type=weapon_type)

    def spawn_health_pack(self, position=None, near_player=False, player_pos=None, heal_amount=25):
        """Spawn a health pack

        Args:
            position (tuple, optional): Specific (x, y) position
            near_player (bool): Whether to spawn near player
            player_pos (tuple, optional): Player position if near_player is True
            heal_amount (int): Amount of health to restore

        Returns:
            HealthPack: The spawned health pack, or None if failed
        """
        return self.spawn_specific_item("health", position, near_player, player_pos, heal_amount=heal_amount)

    def _find_spawn_position(self, near_player=False, player_pos=None, max_attempts=50):
        """Find a valid spawn position

        Args:
            near_player (bool): Whether to spawn near the player
            player_pos (tuple, optional): Player position (x, y)
            max_attempts (int): Maximum attempts to find valid position

        Returns:
            tuple: Valid (x, y) position, or None if not found
        """
        for _ in range(max_attempts):
            if near_player and player_pos:
                # Spawn within a radius of the player
                radius = random.uniform(100, 300)  # 100-300 pixels from player
                angle = random.uniform(0, 2 * math.pi)
                x = player_pos[0] + radius * math.cos(angle)
                y = player_pos[1] + radius * math.sin(angle)
            else:
                # Spawn anywhere on the map
                x = random.uniform(0, MAP_WIDTH * TILE_SIZE)
                y = random.uniform(0, MAP_HEIGHT * TILE_SIZE)

            # Check if position is valid (on grass)
            if self._is_valid_spawn_position(x, y):
                return x, y

        return None

    def _is_valid_spawn_position(self, x, y):
        """Check if position is valid for spawning

        Args:
            x, y (float): Position to check

        Returns:
            bool: True if position is valid for spawning
        """
        # Check bounds
        if x < 0 or x >= MAP_WIDTH * TILE_SIZE or y < 0 or y >= MAP_HEIGHT * TILE_SIZE:
            return False

        # Check tile type (can only spawn on grass)
        tile_type = self.map_generator.get_tile_at(x, y)
        if tile_type != TILE_GRASS:
            return False

        # Check if too close to walls - check surrounding tiles
        wall_check_distance = 64  # Check for walls within this distance
        for check_x in range(int(x - wall_check_distance), int(x + wall_check_distance), 16):
            for check_y in range(int(y - wall_check_distance), int(y + wall_check_distance), 16):
                if check_x < 0 or check_x >= MAP_WIDTH * TILE_SIZE or check_y < 0 or check_y >= MAP_HEIGHT * TILE_SIZE:
                    continue
                check_tile = self.map_generator.get_tile_at(check_x, check_y)
                if check_tile != TILE_GRASS and check_tile != TILE_OBJECT:
                    return False  # Too close to a wall or other non-walkable tile

        # Check if too close to existing items
        for item in self.items:
            distance = math.sqrt((x - item.x) ** 2 + (y - item.y) ** 2)
            if distance < 50:  # Minimum 50 pixels between items
                return False

        return True

    def check_pickups(self, player):
        """Check for item pickups by player

        Args:
            player: Player instance

        Returns:
            list: List of picked up items
        """
        picked_up_items = []

        for item in self.items[:]:  # Use slice to avoid modification during iteration
            if self._is_item_expired(item):
                continue

            # Check collision with player
            distance = math.sqrt((player.x - item.x) ** 2 + (player.y - item.y) ** 2)
            pickup_radius = 40  # Increased pickup radius for better usability

            if distance <= pickup_radius:
                # Try to pickup item using available method
                if self._try_pickup_item(item, player):
                    picked_up_items.append(item)
                    self.items.remove(item)  # Remove from items list after successful pickup

                    # Show pickup notification if UI is available
                    if self.ui:
                        item_name = getattr(item, 'name', None) or getattr(item, 'item_type', 'Item')
                        self.ui.show_pickup_message(f"Picked up {item_name}")

        return picked_up_items

    def render(self, screen, camera_offset):
        """Render all items

        Args:
            screen: Pygame screen surface
            camera_offset: Camera offset (x, y)
        """
        for item in self.items:
            if not self._is_item_expired(item):
                item.render(screen, camera_offset)

    def get_items_info(self):
        """Get information about current items for debugging

        Returns:
            dict: Information about items
        """
        active_items = [item for item in self.items if not self._is_item_expired(item)]

        item_counts = {}
        for item in active_items:
            item_type = item.item_type
            item_counts[item_type] = item_counts.get(item_type, 0) + 1

        return {
            'total_items': len(active_items),
            'max_items': self.max_items,
            'item_types': item_counts,
            'spawn_timer': self.spawn_timer,
            'powerup_timer': self.powerup_spawn_timer
        }

    def clear_all_items(self):
        """Remove all items from the map"""
        self.items.clear()

    def set_spawn_rates(self, item_interval=None, powerup_interval=None):
        """Adjust spawn rates

        Args:
            item_interval (float, optional): New item spawn interval
            powerup_interval (float, optional): New powerup spawn interval
        """
        if item_interval is not None:
            self.spawn_interval = item_interval
        if powerup_interval is not None:
            self.powerup_spawn_interval = powerup_interval
