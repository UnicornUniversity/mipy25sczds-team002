"""
Item Spawner System - Centralized Item Spawning
==============================================

This module provides a centralized system for spawning all types of items in the game.
It replaces the scattered spawn logic found in GameplayState and DropSystem.
"""

import random
import math
from entities.items import Weapon, HealthPack, Powerup
from utils.constants import TILE_SIZE, MAP_WIDTH, MAP_HEIGHT


class ItemSpawner:
    """
    Centralized system for spawning items in the game.
    Handles weapons, health packs, powerups, and their positioning logic.
    """

    def __init__(self, map_generator):
        """Initialize the item spawner.

        Args:
            map_generator: Reference to the map generator for walkable position checks
        """
        self.map_generator = map_generator
        self.items = []

        # Sequential weapon spawning state
        self.current_weapon_tier = 1  # Start with shotgun (index 1 in WEAPON_HIERARCHY)
        self.next_weapon_ready = True  # Flag to indicate if next weapon should be spawned

    def update(self, dt):
        """Update the item spawner.

        Args:
            dt (float): Time delta in seconds
        """
        # Remove picked up items
        self.items = [item for item in self.items if not item.picked_up]

    def spawn_weapon(self, weapon_type, position=None, near_player=False, player_pos=None):
        """Spawn a specific weapon type.

        Args:
            weapon_type (str): Type of weapon to spawn
            position (tuple, optional): Specific (x, y) position to spawn at
            near_player (bool): Whether to spawn near the player
            player_pos (tuple, optional): Player position (x, y) if near_player is True

        Returns:
            Weapon: The spawned weapon, or None if no suitable position was found
        """
        spawn_pos = position or self._find_spawn_position(near_player, player_pos)
        if spawn_pos:
            weapon = Weapon(spawn_pos[0], spawn_pos[1], weapon_type)
            self.items.append(weapon)
            return weapon
        return None

    def spawn_next_tier_weapon(self, current_weapon_type=None):
        """Spawn the next weapon in the tier sequence.

        Args:
            current_weapon_type (str, optional): The weapon type that was just picked up

        Returns:
            Weapon: The spawned weapon, or None if no weapon was spawned
        """
        if not self.next_weapon_ready:
            return None

        # If a current weapon type is provided, advance the tier based on it
        if current_weapon_type:
            try:
                picked_up_tier = Weapon.WEAPON_HIERARCHY.index(current_weapon_type)
                if picked_up_tier == self.current_weapon_tier:
                    self._advance_weapon_tier()
            except ValueError:
                # Weapon type not found in hierarchy, continue with current tier
                pass

        # Get the current weapon type from the hierarchy
        if self.current_weapon_tier < len(Weapon.WEAPON_HIERARCHY):
            weapon_type = Weapon.WEAPON_HIERARCHY[self.current_weapon_tier]

            # Spawn the weapon at a random position
            weapon = self.spawn_weapon(weapon_type)

            if weapon:
                self.next_weapon_ready = False  # Don't spawn another until this one is picked up
                return weapon

        return None

    def spawn_health_pack(self, position=None, near_player=False, player_pos=None):
        """Spawn a health pack.

        Args:
            position (tuple, optional): Specific (x, y) position to spawn at
            near_player (bool): Whether to spawn near the player
            player_pos (tuple, optional): Player position (x, y) if near_player is True

        Returns:
            HealthPack: The spawned health pack, or None if no suitable position was found
        """
        spawn_pos = position or self._find_spawn_position(near_player, player_pos)
        if spawn_pos:
            health_pack = HealthPack(spawn_pos[0], spawn_pos[1])
            self.items.append(health_pack)
            return health_pack
        return None

    def spawn_powerup(self, position=None, near_player=False, player_pos=None):
        """Spawn a powerup.

        Args:
            position (tuple, optional): Specific (x, y) position to spawn at
            near_player (bool): Whether to spawn near the player
            player_pos (tuple, optional): Player position (x, y) if near_player is True

        Returns:
            Powerup: The spawned powerup, or None if no suitable position was found
        """
        spawn_pos = position or self._find_spawn_position(near_player, player_pos)
        if spawn_pos:
            powerup = Powerup(spawn_pos[0], spawn_pos[1])
            self.items.append(powerup)
            return powerup
        return None

    def spawn_random_item(self, position=None, near_player=False, player_pos=None, weapon_type=None):
        """Spawn a random item (health pack or powerup, or specific weapon).

        Args:
            position (tuple, optional): Specific (x, y) position to spawn at
            near_player (bool): Whether to spawn near the player
            player_pos (tuple, optional): Player position (x, y) if near_player is True
            weapon_type (str, optional): Specific weapon type to create, if None a random item is created

        Returns:
            Item: The spawned item, or None if no suitable position was found
        """
        # If a specific weapon type is provided, create that weapon
        if weapon_type is not None:
            return self.spawn_weapon(weapon_type, position, near_player, player_pos)

        # Otherwise, randomly choose between health pack and powerup
        item_type = random.choice(['health', 'powerup'])

        if item_type == 'health':
            return self.spawn_health_pack(position, near_player, player_pos)
        else:
            return self.spawn_powerup(position, near_player, player_pos)

    def spawn_zombie_drop(self, zombie_pos):
        """Spawn an item when a zombie dies (10% chance for health pack or powerup).

        Args:
            zombie_pos (tuple): Position (x, y) where the zombie died

        Returns:
            Item: The spawned item, or None if no item was spawned
        """
        # 10% chance for zombie to drop something
        if random.random() < 0.1:
            # 80% chance for health pack, 20% chance for powerup
            if random.random() < 0.8:
                return self.spawn_health_pack(position=zombie_pos)
            else:
                return self.spawn_powerup(position=zombie_pos)
        return None

    def weapon_picked_up(self, weapon_type):
        """Called when a weapon is picked up to potentially spawn the next tier.

        Args:
            weapon_type (str): Type of weapon that was picked up

        Returns:
            Weapon: The next spawned weapon, or None if no weapon was spawned
        """
        # Mark that the next weapon in sequence is ready to spawn
        self.next_weapon_ready = True

        # Spawn the next tier weapon
        return self.spawn_next_tier_weapon(weapon_type)

    def initialize_weapon_sequence(self):
        """Initialize the weapon sequence by spawning the first weapon (shotgun)."""
        self.current_weapon_tier = 1  # Start with shotgun
        self.next_weapon_ready = True
        return self.spawn_next_tier_weapon()

    def _advance_weapon_tier(self):
        """Advance to the next weapon tier in the sequence."""
        self.current_weapon_tier = (self.current_weapon_tier + 1) % len(Weapon.WEAPON_HIERARCHY)

        # Skip pistol (always at index 0) as it's the starting weapon
        if self.current_weapon_tier == 0:
            self.current_weapon_tier = 1

    def _find_spawn_position(self, near_player=False, player_pos=None):
        """Find a suitable spawn position for an item.

        Args:
            near_player (bool): Whether to find a position near the player
            player_pos (tuple, optional): Player position (x, y) if near_player is True

        Returns:
            tuple: (x, y) position, or None if no suitable position was found
        """
        if near_player and player_pos:
            # Find a position within 10 tiles of the player
            max_distance = 10 * TILE_SIZE
            min_distance = 3 * TILE_SIZE
            center_x, center_y = player_pos
        else:
            # Find a position anywhere on the map
            max_distance = min(MAP_WIDTH, MAP_HEIGHT) * TILE_SIZE / 2
            min_distance = 0
            # Use center of map as reference point
            center_x = (MAP_WIDTH * TILE_SIZE) / 2
            center_y = (MAP_HEIGHT * TILE_SIZE) / 2

        # Try to find a walkable position
        for _ in range(50):  # Limit attempts to avoid infinite loop
            # Random angle
            angle = random.uniform(0, 2 * math.pi)
            # Random distance
            distance = random.uniform(min_distance, max_distance)

            # Calculate position
            x = center_x + distance * math.cos(angle)
            y = center_y + distance * math.sin(angle)

            # Ensure position is within map bounds
            x = max(0, min(x, MAP_WIDTH * TILE_SIZE - TILE_SIZE))
            y = max(0, min(y, MAP_HEIGHT * TILE_SIZE - TILE_SIZE))

            # Check if position is walkable
            if self.map_generator.is_walkable(x, y):
                return (x, y)

        return None

    def remove_item(self, item):
        """Remove an item from the items list.

        Args:
            item: The item to remove
        """
        if item in self.items:
            self.items.remove(item)

    def get_items(self):
        """Get the list of items.

        Returns:
            list: List of items
        """
        return self.items

    def clear_items(self):
        """Clear all items."""
        self.items = []