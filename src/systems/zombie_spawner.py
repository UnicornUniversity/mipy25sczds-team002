import random
import math
from entities.zombies import Zombie
from utils.constants import (
    TILE_SIZE, MAP_WIDTH, MAP_HEIGHT, WINDOW_WIDTH, WINDOW_HEIGHT,
    INITIAL_MAX_ZOMBIES, MAX_ZOMBIES_CAP, ZOMBIE_SPAWN_RATE_INITIAL,
    ZOMBIE_SPAWN_RATE_MIN, ZOMBIE_SPAWN_RATE_DECREASE, ZOMBIE_MAX_INCREASE_RATE,
    ZOMBIE_SPAWN_DISTANCE_MIN, ZOMBIE_SPAWN_DISTANCE_MAX
)

class ZombieSpawner:
    """Handles zombie spawning with difficulty scaling"""
    
    def __init__(self, map_generator):
        """Initialize the zombie spawner
        
        Args:
            map_generator: Reference to the map generator for walkable tile checks
        """
        self.map_generator = map_generator
        self.game_time = 0  # Time elapsed in seconds
        self.spawn_timer = 0  # Timer for next spawn
        self.zombies = []  # List of active zombies
        self.max_zombies = INITIAL_MAX_ZOMBIES  # Initial max zombies
        self.base_spawn_rate = ZOMBIE_SPAWN_RATE_INITIAL  # Base spawn rate in seconds
        
        # Calculate minimum spawn distance to be outside visible area
        # Use screen diagonal as minimum distance to ensure spawning outside view
        screen_diagonal = math.sqrt(WINDOW_WIDTH**2 + WINDOW_HEIGHT**2)
        self.min_spawn_distance = int(screen_diagonal * ZOMBIE_SPAWN_DISTANCE_MIN)
        self.max_spawn_distance = int(screen_diagonal * ZOMBIE_SPAWN_DISTANCE_MAX)
        
        # Calculate map boundaries in pixels
        self.map_width_px = int(MAP_WIDTH * TILE_SIZE)
        self.map_height_px = int(MAP_HEIGHT * TILE_SIZE)
        
    def update(self, dt, player_x, player_y):
        """Update spawner state and spawn new zombies if needed
        
        Args:
            dt (float): Time delta in seconds
            player_x (float): Player's x position
            player_y (float): Player's y position
        """
        # Update game time
        self.game_time += dt
        
        # Update spawn timer
        self.spawn_timer += dt
        
        # Calculate current spawn rate based on game time
        current_spawn_rate = self._calculate_spawn_rate()
        
        # Spawn new zombie if timer exceeds spawn rate and we haven't reached max zombies
        if self.spawn_timer >= current_spawn_rate and len(self.zombies) < self.max_zombies:
            self._spawn_zombie(player_x, player_y)
            self.spawn_timer = 0
            
        # Update max zombies based on game time
        self.max_zombies = self._calculate_max_zombies()
        
    def _calculate_spawn_rate(self):
        """Calculate current spawn rate based on game time
        
        Returns:
            float: Current spawn rate in seconds
        """
        # Decrease spawn rate over time (minimum ZOMBIE_SPAWN_RATE_MIN seconds)
        return max(ZOMBIE_SPAWN_RATE_MIN, 
                  self.base_spawn_rate - (self.game_time / ZOMBIE_SPAWN_RATE_DECREASE))
        
    def _calculate_max_zombies(self):
        """Calculate maximum number of zombies based on game time
        
        Returns:
            int: Maximum number of zombies allowed
        """
        # Increase max zombies over time
        return min(MAX_ZOMBIES_CAP, 
                  INITIAL_MAX_ZOMBIES + int(self.game_time / ZOMBIE_MAX_INCREASE_RATE))
        
    def _spawn_zombie(self, player_x, player_y):
        """Spawn a new zombie at a valid position
        
        Args:
            player_x (float): Player's x position
            player_y (float): Player's y position
        """
        # Try to find a valid spawn position
        for _ in range(10):  # Try up to 10 times
            # Calculate random angle and distance
            angle = random.uniform(0, 2 * math.pi)
            distance = random.uniform(self.min_spawn_distance, self.max_spawn_distance)
            
            # Calculate spawn position
            spawn_x = int(player_x + math.cos(angle) * distance)
            spawn_y = int(player_y + math.sin(angle) * distance)
            
            # Ensure spawn position is within map bounds
            spawn_x = max(0, min(spawn_x, self.map_width_px))
            spawn_y = max(0, min(spawn_y, self.map_height_px))
            
            # Check if position is walkable
            if self.map_generator.is_walkable(spawn_x, spawn_y):
                # Create and add new zombie
                zombie = Zombie(spawn_x, spawn_y)
                self.zombies.append(zombie)
                break
                
    def get_zombies(self):
        """Get list of active zombies
        
        Returns:
            list: List of active zombies
        """
        return self.zombies
        
    def remove_zombie(self, zombie):
        """Remove a zombie from the active list
        
        Args:
            zombie: Zombie instance to remove
        """
        if zombie in self.zombies:
            self.zombies.remove(zombie) 