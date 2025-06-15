import random
import math
from entities.zombies import Zombie
from systems import collisions
from utils.constants import (
    TILE_SIZE, MAP_WIDTH, MAP_HEIGHT, WINDOW_WIDTH, WINDOW_HEIGHT,
    INITIAL_MAX_ZOMBIES, MAX_ZOMBIES_CAP, ZOMBIE_SPAWN_RATE_INITIAL,
    ZOMBIE_SPAWN_RATE_MIN, ZOMBIE_SPAWN_RATE_DECREASE_INTERVAL, ZOMBIE_SPAWN_RATE_DECREASE_AMOUNT,
    ZOMBIE_MAX_INCREASE_RATE, INITIAL_ZOMBIE_COUNT,
    ZOMBIE_SPAWN_DISTANCE_MIN, ZOMBIE_SPAWN_DISTANCE_MAX
)


class EnemySpawner:
    """Handles enemy spawning with difficulty scaling"""

    def __init__(self, map_generator):
        """Initialize the enemy system

        Args:
            map_generator: Reference to the map generator for walkable tile checks
        """
        self.map_generator = map_generator
        self.game_time = 0  # Time elapsed in seconds
        self.spawn_timer = 0  # Timer for next spawn
        self.zombies = []  # List of active zombies
        self.max_zombies = INITIAL_MAX_ZOMBIES  # Initial max zombies
        self.current_spawn_rate = ZOMBIE_SPAWN_RATE_INITIAL  # Current spawn rate in seconds
        self.time_since_last_decrease = 0  # Time since last spawn rate decrease

        # Calculate minimum spawn distance to be outside visible area
        # Use screen diagonal as minimum distance to ensure spawning outside view
        screen_diagonal = math.sqrt(WINDOW_WIDTH ** 2 + WINDOW_HEIGHT ** 2)
        self.min_spawn_distance = int(screen_diagonal * ZOMBIE_SPAWN_DISTANCE_MIN)
        self.max_spawn_distance = int(screen_diagonal * ZOMBIE_SPAWN_DISTANCE_MAX)

        # Calculate map boundaries in pixels
        self.map_width_px = int(MAP_WIDTH * TILE_SIZE)
        self.map_height_px = int(MAP_HEIGHT * TILE_SIZE)

        # Spawn initial zombies
        self._spawn_initial_zombies()

    def _spawn_initial_zombies(self):
        """Spawn initial zombies at game start"""
        for _ in range(INITIAL_ZOMBIE_COUNT):
            # Find a random position on the map
            x = random.randint(0, self.map_width_px)
            y = random.randint(0, self.map_height_px)

            # Ensure position is within map bounds and walkable
            x = max(0, min(x, self.map_width_px))
            y = max(0, min(y, self.map_height_px))

            if self.map_generator.is_walkable(x, y):
                zombie = Zombie(x, y)
                self.zombies.append(zombie)

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

        # Update time since last spawn rate decrease
        self.time_since_last_decrease += dt

        # Decrease spawn rate every ZOMBIE_SPAWN_RATE_DECREASE_INTERVAL seconds
        if self.time_since_last_decrease >= ZOMBIE_SPAWN_RATE_DECREASE_INTERVAL:
            self.current_spawn_rate = max(ZOMBIE_SPAWN_RATE_MIN,
                                          self.current_spawn_rate - ZOMBIE_SPAWN_RATE_DECREASE_AMOUNT)
            self.time_since_last_decrease = 0

        for zombie in self.zombies[:]:
            # Normal movement update
            zombie.update(dt, player_x, player_y, self.map_generator)

            # Resolve zombie-zombie collisions
            new_x, new_y = collisions.check_zombie_collisions(zombie, self.zombies)
            zombie.x = new_x
            zombie.y = new_y

            # Update zombie's rect position manually (without calling full update)
            zombie.rect.x = int(zombie.x)
            zombie.rect.y = int(zombie.y)

        # Spawn new zombie if timer exceeds spawn rate and we haven't reached max zombies
        if self.spawn_timer >= self.current_spawn_rate and len(self.zombies) < self.max_zombies:
            self._spawn_zombie(player_x, player_y)
            self.spawn_timer = 0

        # Update max zombies based on game time
        self.max_zombies = self._calculate_max_zombies()

    def render(self, screen, camera_offset=(0, 0)):
        """Render all zombies"""
        for zombie in self.zombies:
            zombie.render(screen, camera_offset)

    def get_zombies(self):
        """Get list of all active zombies"""
        return self.zombies

    def remove_zombie(self, zombie):
        """Remove zombie from the list"""
        if zombie in self.zombies:
            self.zombies.remove(zombie)

    def _calculate_max_zombies(self):
        """Calculate maximum number of zombies based on game time

        Returns:
            int: Maximum number of zombies allowed
        """
        # Increase max zombies over time
        return min(MAX_ZOMBIES_CAP,
                   INITIAL_MAX_ZOMBIES + int(self.game_time / ZOMBIE_MAX_INCREASE_RATE))

    def _spawn_zombie(self, player_x, player_y):
        """Spawn a new zombie at a valid position with collision check

        Args:
            player_x (float): Player's x position
            player_y (float): Player's y position
        """
        # Try to find a valid spawn position
        for _ in range(20):  # Try up to 20 times (increased from 10)
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
                # Determine zombie type based on weighted probability
                # 60% normal, 20% fast, 20% tough
                rand_value = random.random()

                if rand_value < 0.6:  # 60% chance for normal zombie
                    temp_zombie = Zombie(spawn_x, spawn_y)
                    zombie_type = "weak"
                elif rand_value < 0.8:  # 20% chance for fast zombie (0.6 to 0.8)
                    from entities.zombies import FastZombie
                    temp_zombie = FastZombie(spawn_x, spawn_y)
                    zombie_type = "fast"
                else:  # 20% chance for tough zombie (0.8 to 1.0)
                    from entities.zombies import ToughZombie
                    temp_zombie = ToughZombie(spawn_x, spawn_y)
                    zombie_type = "tough"

                # Check if there's enough space (no collision with other zombies)
                collision_detected = False
                for existing_zombie in self.zombies:
                    dx = temp_zombie.x - existing_zombie.x
                    dy = temp_zombie.y - existing_zombie.y
                    distance_to_existing = math.sqrt(dx * dx + dy * dy)

                    # Require minimum distance between zombies at spawn
                    if distance_to_existing < 40:  # 40 pixels minimum distance
                        collision_detected = True
                        break

                # If no collision, spawn the zombie
                if not collision_detected:
                    self.zombies.append(temp_zombie)
                    print(f"Spawned {zombie_type} zombie! (Total: {len(self.zombies)})")
                    break