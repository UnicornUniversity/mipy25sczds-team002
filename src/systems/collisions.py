"""
Collision System - Centralized Collision Detection and Resolution
================================================================

This module provides a centralized system for handling all collision detection
and resolution in the game. It ensures consistent collision behavior across
different entity types and provides a unified interface for collision checks.
"""

import math
from utils.constants import (
    TILE_GRASS, TILE_OBJECT, TILE_WOOD,
    ZOMBIE_COLLISION_RADIUS
)

class CollisionSystem:
    """
    Centralized system for handling all collision detection and resolution in the game.
    """

    def __init__(self, map_generator):
        """Initialize the collision system.

        Args:
            map_generator: Reference to the map generator for tile-based collision checks
        """
        self.map_generator = map_generator

    def check_entity_collision(self, entity1, entity2):
        """Check if two entities are colliding.

        Args:
            entity1: First entity
            entity2: Second entity

        Returns:
            bool: True if entities are colliding, False otherwise
        """
        # Calculate distance between entity centers
        dx = entity1.x + entity1.width/2 - (entity2.x + entity2.width/2)
        dy = entity1.y + entity1.height/2 - (entity2.y + entity2.height/2)
        distance = (dx * dx + dy * dy) ** 0.5

        # Increase pickup radius for items and weapons
        pickup_radius_multiplier = 1.0

        # Check if either entity is an item (has item_type attribute)
        if hasattr(entity1, 'item_type') or hasattr(entity2, 'item_type'):
            pickup_radius_multiplier = 2.0  # Double the pickup radius for items

        # Check if distance is less than sum of radii (using width as diameter)
        return distance < (entity1.width + entity2.width) / 2 * pickup_radius_multiplier

    def check_entity_list_collision(self, entity, entity_list):
        """Check if an entity is colliding with any entity in a list.

        Args:
            entity: The entity to check
            entity_list: List of entities to check against

        Returns:
            tuple: (bool, entity) - True and the colliding entity if collision detected, False and None otherwise
        """
        for other_entity in entity_list:
            if self.check_entity_collision(entity, other_entity):
                return True, other_entity
        return False, None

    def is_position_walkable(self, x, y):
        """Check if the specified world coordinates are walkable.

        Entities can walk on floor (TILE_GRASS), objects (TILE_OBJECT), and wood (TILE_WOOD) but not on walls.

        Args:
            x (float): X coordinate in world space
            y (float): Y coordinate in world space

        Returns:
            bool: True if position is walkable, False otherwise
        """
        if not self.map_generator:
            return True  # If no map generator, assume all positions are walkable

        tile_type = self.map_generator.get_tile_at(x, y)

        # Entities can walk on floor (TILE_GRASS), objects (TILE_OBJECT), and wood (TILE_WOOD) but not on walls
        return tile_type == TILE_GRASS or tile_type == TILE_OBJECT or tile_type == TILE_WOOD

    def check_wall_collision(self, entity, new_x, new_y):
        """Check if an entity would collide with a wall at the specified position.

        Args:
            entity: The entity to check
            new_x (float): New X coordinate to check
            new_y (float): New Y coordinate to check

        Returns:
            bool: True if collision with wall detected, False otherwise
        """
        if not self.map_generator:
            return False  # If no map generator, assume no wall collisions

        # Check the center of the entity
        center_x = new_x + entity.width / 2
        center_y = new_y + entity.height / 2

        # Check if the center position is walkable
        return not self.is_position_walkable(center_x, center_y)

    def resolve_movement(self, entity, dx, dy, dt, speed):
        """Resolve entity movement with collision detection.

        Args:
            entity: The entity to move
            dx (float): X direction (-1 to 1)
            dy (float): Y direction (-1 to 1)
            dt (float): Time delta in seconds
            speed (float): Movement speed in pixels per second

        Returns:
            tuple: (new_x, new_y, collided) - New position and whether a collision occurred
        """
        # Calculate new position
        distance = math.sqrt(dx * dx + dy * dy) if (dx != 0 or dy != 0) else 1
        normalized_dx = dx / distance if distance > 0 else 0
        normalized_dy = dy / distance if distance > 0 else 0

        move_x = normalized_dx * speed * dt
        move_y = normalized_dy * speed * dt

        new_x = entity.x + move_x
        new_y = entity.y + move_y

        # Check for wall collision in X direction
        if self.check_wall_collision(entity, new_x, entity.y):
            # If X movement would cause collision, try to slide along the wall in Y direction
            new_x = entity.x
            if not self.check_wall_collision(entity, new_x, new_y):
                # Y movement is valid, allow sliding
                pass
            else:
                # Both X and Y movement cause collision, don't move
                new_y = entity.y
                return entity.x, entity.y, True

        # Check for wall collision in Y direction
        if self.check_wall_collision(entity, new_x, new_y):
            # If Y movement would cause collision, try to slide along the wall in X direction
            new_y = entity.y
            if not self.check_wall_collision(entity, new_x, new_y):
                # X movement is valid, allow sliding
                pass
            else:
                # Both X and Y movement cause collision, don't move
                new_x = entity.x
                return entity.x, entity.y, True

        return new_x, new_y, False

    @staticmethod
    def check_zombie_collisions(zombie, zombies):
        """Check and resolve collisions between zombies.

        Args:
            zombie: The zombie to check
            zombies: List of all zombies

        Returns:
            tuple: (new_x, new_y) - New position after resolving collisions
        """
        new_x, new_y = zombie.x, zombie.y

        for other_zombie in zombies:
            if zombie == other_zombie:
                continue  # Skip self

            # Calculate distance between zombie centers
            dx = (zombie.x + zombie.width/2) - (other_zombie.x + other_zombie.width/2)
            dy = (zombie.y + zombie.height/2) - (other_zombie.y + other_zombie.height/2)
            distance = math.sqrt(dx * dx + dy * dy)

            # If zombies are too close, push them apart
            min_distance = ZOMBIE_COLLISION_RADIUS * 2
            if min_distance > distance > 0:  # Avoid division by zero
                # Calculate push direction and force
                push_x = dx / distance
                push_y = dy / distance
                push_force = (min_distance - distance) * 0.5

                # Move zombie away from other zombie
                new_x += push_x * push_force
                new_y += push_y * push_force

        return new_x, new_y

# Create a global instance for convenience
collision_system = None

def initialize(map_generator):
    """Initialize the collision system with the map generator.

    Args:
        map_generator: Reference to the map generator
    """
    global collision_system
    collision_system = CollisionSystem(map_generator)

def check_entity_collision(entity1, entity2):
    """Convenience function to check if two entities are colliding."""
    if collision_system:
        return collision_system.check_entity_collision(entity1, entity2)
    return False

def check_entity_list_collision(entity, entity_list):
    """Convenience function to check if an entity is colliding with any entity in a list."""
    if collision_system:
        return collision_system.check_entity_list_collision(entity, entity_list)
    return False, None

def is_position_walkable(x, y):
    """Convenience function to check if a position is walkable."""
    if collision_system:
        return collision_system.is_position_walkable(x, y)
    return True

def check_wall_collision(entity, new_x, new_y):
    """Convenience function to check if an entity would collide with a wall."""
    if collision_system:
        return collision_system.check_wall_collision(entity, new_x, new_y)
    return False

def resolve_movement(entity, dx, dy, dt, speed):
    """Convenience function to resolve entity movement with collision detection."""
    if collision_system:
        return collision_system.resolve_movement(entity, dx, dy, dt, speed)
    # If no collision system, just move without collision detection
    new_x = entity.x + dx * speed * dt
    new_y = entity.y + dy * speed * dt
    return new_x, new_y, False

def check_zombie_collisions(zombie, zombies):
    """Convenience function to check and resolve collisions between zombies."""
    if collision_system:
        return collision_system.check_zombie_collisions(zombie, zombies)
    return zombie.x, zombie.y
