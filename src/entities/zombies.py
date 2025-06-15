import math
import pygame
import random
from entities.entity import Entity
from utils.constants import (
    # Zombie sizes
    ENEMY_SIZE, TOUGH_ZOMBIE_SIZE, FAST_ZOMBIE_SIZE,

    # Zombie speeds
    ZOMBIE_SPEED_MIN, ZOMBIE_SPEED_MAX,
    TOUGH_ZOMBIE_SPEED_MIN, TOUGH_ZOMBIE_SPEED_MAX,
    FAST_ZOMBIE_SPEED_MIN, FAST_ZOMBIE_SPEED_MAX,

    # Zombie health
    ZOMBIE_HEALTH, TOUGH_ZOMBIE_HEALTH, FAST_ZOMBIE_HEALTH,

    # Zombie damage
    ZOMBIE_DAMAGE, TOUGH_ZOMBIE_DAMAGE, FAST_ZOMBIE_DAMAGE,

    # Zombie combat
    ZOMBIE_ATTACK_RANGE, ZOMBIE_ATTACK_COOLDOWN, ZOMBIE_ATTACK_DURATION,

    # Zombie scores
    ZOMBIE_SCORE, TOUGH_ZOMBIE_SCORE, FAST_ZOMBIE_SCORE,

    # Map constants
    TILE_OBJECT, OBJECT_SPEED_MULTIPLIER,

    # Colors
    BLACK, RED, BLUE, ZOMBIE_MIN_MOVEMENT_DISTANCE, YELLOW, WINDOW_WIDTH, WINDOW_HEIGHT,
    MAP_WIDTH, TILE_SIZE, MAP_HEIGHT
)


class Zombie(Entity):
    """Zombie entity that follows the player"""

    def __init__(self, x, y):
        """Initialize the zombie

        Args:
            x (float): Initial x position
            y (float): Initial y position
        """
        super().__init__(x, y, ENEMY_SIZE, ENEMY_SIZE, BLACK)
        # Random speed for weak zombies
        import random
        self.speed = random.uniform(ZOMBIE_SPEED_MIN, ZOMBIE_SPEED_MAX)
        self.is_on_object = False
        self.map_generator = None
        self.health = ZOMBIE_HEALTH
        self.attack_timer = 0
        self.is_attacking = False
        self.attack_animation_timer = 0

        # Animation tracking for sprites
        self.animation_time = 0
        self.is_moving = False

        # Direction tracking for sprite flipping
        self.facing_left = False  # True if facing left, False if facing right

        # Movement angle for sprite rotation
        self.movement_angle = 0  # Angle in radians (0 = right, pi/2 = down)
        self.attack_angle = 0  # Angle when attacking (preserved during attack)

        # Stuck detection and pathfinding
        self.stuck_timer = 0.0
        self.last_position = (x, y)
        self.stuck_check_interval = 0.5  # Check every 0.5 seconds
        self.stuck_counter = 0.0
        self.is_force_pathfinding = False
        self.force_target = None
        self.force_pathfind_timer = 0.0

        # Sound effects
        self.groan_timer = 0.0
        self.groan_interval = random.uniform(5.0, 15.0)  # Random interval between groans

    def update(self, dt, player_x=None, player_y=None, map_generator=None):
        """Update zombie state to move towards player

        Args:
            dt (float): Time delta in seconds
            player_x (float, optional): Player's x position
            player_y (float, optional): Player's y position
            map_generator (MapGenerator, optional): Reference to the map generator
        """
        # Call parent update first to handle rect position
        super().update(dt)

        # Update groan timer
        self.groan_timer += dt
        if self.groan_timer >= self.groan_interval:
            # Reset timer with a new random interval
            self.groan_timer = 0
            self.groan_interval = random.uniform(5.0, 15.0)

            # Play zombie groan sound (with a chance to not play to avoid too many sounds)
            if random.random() < 0.3 and player_x is not None:  # 30% chance to groan when player is in game
                from systems.audio import music_manager
                music_manager.play_sound("zombies_zombie_groan", volume=0.4)  # Lower volume for ambient groans

        # If no player position provided, just update timers
        if player_x is None or player_y is None:
            # Update attack timer
            if self.attack_timer > 0:
                self.attack_timer -= dt

            # Update attack animation
            if self.is_attacking:
                self.attack_animation_timer -= dt
                if self.attack_animation_timer <= 0:
                    self.is_attacking = False
            return

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

        # Check if stuck and teleport if needed
        if self.check_if_stuck(dt, player_x, player_y):
            self.trigger_force_pathfinding(player_x, player_y)

        # Handle normal movement
        self._handle_movement(dt, player_x, player_y)

        # Update animation time
        if self.is_moving:
            self.animation_time += dt
        else:
            self.animation_time = 0

    def trigger_force_pathfinding(self, player_x, player_y):
        """Teleport zombie just outside screen but closer to player when stuck

        Args:
            player_x (float): Player x position
            player_y (float): Player y position
        """
        print(f"Zombie at ({int(self.x)}, {int(self.y)}) is stuck! Teleporting just outside screen closer to player...")

        # Reset stuck counter
        self.stuck_counter = 0

        import random
        import math

        # Try to find a good teleport position just outside screen but closer than current position
        current_distance_to_player = math.sqrt((self.x - player_x) ** 2 + (self.y - player_y) ** 2)
        target_distance = min(current_distance_to_player * 0.8, 400)  # 80% of current distance, max 400px

        # Calculate minimum distance to be just off-screen
        min_off_screen_distance = max(WINDOW_WIDTH, WINDOW_HEIGHT) // 2 + 100  # Just outside visible area

        for attempt in range(30):
            # Random angle around the player
            angle = random.uniform(0, 2 * math.pi)

            # Distance from player (closer than current but still just off-screen)
            distance = max(min_off_screen_distance,
                           random.uniform(target_distance * 0.9, target_distance * 1.1))

            # Calculate potential teleport position
            teleport_x = player_x + distance * math.cos(angle)
            teleport_y = player_y + distance * math.sin(angle)

            # Check if position is just outside screen (not too far)
            distance_from_player = math.sqrt((teleport_x - player_x) ** 2 + (teleport_y - player_y) ** 2)
            is_just_off_screen = (min_off_screen_distance <= distance_from_player <= 500)  # Max 500px from player

            # Check if position is walkable
            is_walkable = True
            if self.map_generator:
                is_walkable = self.map_generator.is_walkable(teleport_x, teleport_y)

            # Check if position is within map bounds
            map_width_px = MAP_WIDTH * TILE_SIZE
            map_height_px = MAP_HEIGHT * TILE_SIZE
            is_in_map = (50 <= teleport_x <= map_width_px - 50 and
                         50 <= teleport_y <= map_height_px - 50)

            if is_just_off_screen and is_walkable and is_in_map:
                # Teleport the zombie
                self.x = teleport_x
                self.y = teleport_y
                self.rect.x = int(self.x)
                self.rect.y = int(self.y)

                print(
                    f"Zombie teleported just off-screen to ({int(self.x)}, {int(self.y)}) - distance: {int(distance)}px")
                return

        # Fallback: Place zombie at the edge of visible area in cardinal directions
        # Choose the direction that's closest to the zombie's current position
        directions = [
            (player_x - min_off_screen_distance, player_y, "left"),
            (player_x + min_off_screen_distance, player_y, "right"),
            (player_x, player_y - min_off_screen_distance, "up"),
            (player_x, player_y + min_off_screen_distance, "down")
        ]

        # Find the closest valid direction
        best_direction = None
        best_distance = float('inf')

        for dir_x, dir_y, name in directions:
            # Check if position is within map bounds
            map_width_px = MAP_WIDTH * TILE_SIZE
            map_height_px = MAP_HEIGHT * TILE_SIZE
            if 50 <= dir_x <= map_width_px - 50 and 50 <= dir_y <= map_height_px - 50:
                # Check if walkable
                if self.map_generator and self.map_generator.is_walkable(dir_x, dir_y):
                    dist_to_zombie = math.sqrt((dir_x - self.x) ** 2 + (dir_y - self.y) ** 2)
                    if dist_to_zombie < best_distance:
                        best_distance = dist_to_zombie
                        best_direction = (dir_x, dir_y, name)

        if best_direction:
            self.x = best_direction[0]
            self.y = best_direction[1]
            self.rect.x = int(self.x)
            self.rect.y = int(self.y)

            final_distance = math.sqrt((self.x - player_x) ** 2 + (self.y - player_y) ** 2)
            print(
                f"Zombie teleported to {best_direction[2]} edge at ({int(self.x)}, {int(self.y)}) - distance: {int(final_distance)}px")
        else:
            # Last resort: just move closer to player but stay off-screen
            angle = math.atan2(player_y - self.y, player_x - self.x)
            self.x = player_x + min_off_screen_distance * math.cos(angle + math.pi)  # Opposite direction
            self.y = player_y + min_off_screen_distance * math.sin(angle + math.pi)
            self.rect.x = int(self.x)
            self.rect.y = int(self.y)

            final_distance = math.sqrt((self.x - player_x) ** 2 + (self.y - player_y) ** 2)
            print(
                f"Zombie last-resort teleported to ({int(self.x)}, {int(self.y)}) - distance: {int(final_distance)}px")

    def check_if_stuck(self, dt, player_x, player_y):
        """Check if zombie is stuck and needs teleportation

        Args:
            dt (float): Time delta
            player_x (float): Player x position
            player_y (float): Player y position

        Returns:
            bool: True if zombie should be teleported
        """
        self.stuck_timer += dt

        if self.stuck_timer >= self.stuck_check_interval:
            # Calculate distance moved since last check
            distance_moved = math.sqrt(
                (self.x - self.last_position[0]) ** 2 +
                (self.y - self.last_position[1]) ** 2
            )

            # Check distance to player
            distance_to_player = math.sqrt((self.x - player_x) ** 2 + (self.y - player_y) ** 2)

            # ONLY allow teleportation if zombie is FAR from player (off-screen)
            is_far_from_player = distance_to_player > 500  # More than 500px from player

            # Check if zombie is trying to move towards player but not moving much
            should_be_moving = distance_to_player > 50  # Should move if more than 50 pixels away

            if should_be_moving and distance_moved < ZOMBIE_MIN_MOVEMENT_DISTANCE and is_far_from_player:
                # Zombie should be moving but isn't AND is far from player - increment stuck counter
                self.stuck_counter += self.stuck_check_interval

                # Shorter timeout for faster teleportation
                if self.stuck_counter >= 1.0:  # Only 1 second instead of 2
                    return True  # Trigger teleportation
            else:
                # Zombie is moving or doesn't need to move OR is too close to player - reset stuck counter
                self.stuck_counter = 0

            # Update position tracking
            self.last_position = (self.x, self.y)
            self.stuck_timer = 0

        return False

    def _handle_movement(self, dt, player_x, player_y):
        """Handle zombie movement - simplified without complex pathfinding

        Args:
            dt (float): Time delta
            player_x (float): Player x position
            player_y (float): Player y position
        """
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

        # Only move if not already at target position and not attacking
        if distance > 5 and not self.is_attacking:  # Small threshold to prevent jittering
            dx /= distance
            dy /= distance

            # Use the collision system to resolve movement with wall collision detection
            from systems.collisions import resolve_movement
            new_x, new_y, collided = resolve_movement(self, dx, dy, dt, base_speed)
            self.x, self.y = new_x, new_y

            self.is_moving = True

            # Update facing direction based on horizontal movement
            if dx < -0.1:  # Moving left (with small threshold to avoid jittering)
                self.facing_left = True
            elif dx > 0.1:  # Moving right
                self.facing_left = False

            # Calculate movement angle for sprite rotation
            self.movement_angle = math.atan2(dy, dx)

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
                # Store the attack angle (direction towards player when attack starts)
                self.attack_angle = math.atan2(dy, dx)

                # Start attack animation
                self.is_attacking = True
                self.attack_animation_timer = ZOMBIE_ATTACK_DURATION

                # Reset attack timer
                self.attack_timer = ZOMBIE_ATTACK_COOLDOWN

                # Play zombie attack sound
                from systems.audio import music_manager
                music_manager.play_sound("zombies_zombie_attack")

                # Deal damage to player
                if player.take_damage(ZOMBIE_DAMAGE):
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

        # Get zombie sprite from texture atlas - use stand sprite during attack, hold sprite otherwise
        sprite_name = 'zoimbie1_stand' if self.is_attacking else 'zoimbie1_hold'
        from utils.sprite_loader import get_texture
        sprite = get_texture('zombie', sprite_name)
        if not sprite:
            # Fallback to old sprite system
            from utils.sprite_loader import get_sprite
            sprite = get_sprite('zombie_basic_1')

        if sprite:
            # Apply color tint for different zombie types (implemented in subclasses)
            sprite = self._apply_zombie_tint(sprite)

            # Use attack angle during attack, movement angle otherwise
            angle_to_use = self.attack_angle if self.is_attacking else self.movement_angle

            # Convert angle from radians to degrees for rotation
            rotation_angle = math.degrees(-angle_to_use)

            # Rotate the zombie sprite
            import pygame
            rotated_sprite = pygame.transform.rotate(sprite, rotation_angle)

            # Calculate position to center the rotated sprite on the zombie
            sprite_x = center_x - rotated_sprite.get_width() // 2
            sprite_y = center_y - rotated_sprite.get_height() // 2

            # Visual indicator for force pathfinding (optional debug)
            color_tint = None
            if self.is_force_pathfinding:
                color_tint = (255, 255, 0, 100)  # Yellow tint when force pathfinding

            # Apply transparency if on object
            if self.is_on_object:
                # Create a copy with alpha for transparency effect
                rotated_sprite_copy = rotated_sprite.copy()
                rotated_sprite_copy.set_alpha(180)  # Semi-transparent
                screen.blit(rotated_sprite_copy, (sprite_x, sprite_y))
            else:
                # Optional: slight visual feedback for movement
                if self.is_moving and not self.is_attacking:
                    # Enhanced wobble effect during movement
                    wobble_offset = int(3 * abs(math.sin(self.animation_time * 6)))
                    sprite_x += wobble_offset

                # Add attack animation
                if self.is_attacking:
                    # Scale up slightly during attack but keep the same rotation
                    scale = 1.2
                    attack_sprite = pygame.transform.scale(rotated_sprite,
                                                           (int(rotated_sprite.get_width() * scale),
                                                            int(rotated_sprite.get_height() * scale)))
                    # Center the scaled sprite
                    attack_sprite_x = center_x - attack_sprite.get_width() // 2
                    attack_sprite_y = center_y - attack_sprite.get_height() // 2
                    screen.blit(attack_sprite, (attack_sprite_x, attack_sprite_y))
                else:
                    screen.blit(rotated_sprite, (sprite_x, sprite_y))

                # Apply color tint for force pathfinding (debug visual)
                if color_tint:
                    tint_surface = pygame.Surface(rotated_sprite.get_size(), pygame.SRCALPHA)
                    tint_surface.fill(color_tint)
                    screen.blit(tint_surface, (sprite_x, sprite_y))

        else:
            # Fallback: draw circle if sprite not available
            if self.is_on_object:
                # Create a transparent surface for the zombie when on an object
                import pygame
                circle_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
                # Draw a semi-transparent circle (128 is 50% opacity)
                pygame.draw.circle(circle_surface, (*self.color, 128), (self.width // 2, self.height // 2),
                                   self.width // 2)
                # Blit the surface to the screen
                screen.blit(circle_surface, (center_x - self.width // 2, center_y - self.height // 2))
            else:
                # Draw zombie normally when not on an object
                color = YELLOW if self.is_force_pathfinding else self.color  # Yellow when force pathfinding
                import pygame
                pygame.draw.circle(screen, color, (center_x, center_y), self.width // 2)

    def _apply_zombie_tint(self, sprite):
        """Apply color tint to zombie sprite based on zombie type

        Args:
            sprite (pygame.Surface): Original sprite

        Returns:
            pygame.Surface: Tinted sprite
        """
        # Base zombie has no tint
        return sprite

    def get_score_value(self):
        """Get the score value for killing this zombie type

        Returns:
            int: Score value
        """
        return ZOMBIE_SCORE

class ToughZombie(Zombie):
    """Tough zombie entity that is large and very strong"""

    def __init__(self, x, y):
        """Initialize the tough zombie

        Args:
            x (float): Initial x position
            y (float): Initial y position
        """
        # Call parent constructor but override size
        super().__init__(x, y)

        # Override size for tough zombie (bigger)
        self.width = TOUGH_ZOMBIE_SIZE
        self.height = TOUGH_ZOMBIE_SIZE
        self.rect = pygame.Rect(x, y, self.width, self.height)

        # Override properties for tough zombie
        self.color = RED  # Red color for tough zombies
        # Random speed for tough zombies (slower range)
        self.speed = random.uniform(TOUGH_ZOMBIE_SPEED_MIN, TOUGH_ZOMBIE_SPEED_MAX)
        self.health = TOUGH_ZOMBIE_HEALTH

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
                # Store the attack angle (direction towards player when attack starts)
                self.attack_angle = math.atan2(dy, dx)

                # Start attack animation
                self.is_attacking = True
                self.attack_animation_timer = ZOMBIE_ATTACK_DURATION

                # Reset attack timer
                self.attack_timer = ZOMBIE_ATTACK_COOLDOWN

                # Play zombie attack sound
                from systems.audio import music_manager
                music_manager.play_sound("zombies_zombie_attack")

                # Deal damage to player (more damage than regular zombie)
                if player.take_damage(TOUGH_ZOMBIE_DAMAGE):
                    return True

        return False

    def render(self, screen, camera_offset=(0, 0)):
        """Render the tough zombie with larger size

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

        # Get zombie sprite from texture atlas - use stand sprite during attack, hold sprite otherwise
        sprite_name = 'zoimbie1_stand' if self.is_attacking else 'zoimbie1_hold'
        from utils.sprite_loader import get_texture
        sprite = get_texture('zombie', sprite_name)
        if not sprite:
            # Fallback to old sprite system
            from utils.sprite_loader import get_sprite
            sprite = get_sprite('zombie_tank_1')

        if sprite:
            # Apply red tint for tough zombie
            sprite = self._apply_zombie_tint(sprite)

            # Scale up sprite for tough zombie (make it bigger)
            scale_factor = TOUGH_ZOMBIE_SIZE / ENEMY_SIZE  # Scale based on size ratio
            scaled_size = (int(sprite.get_width() * scale_factor), int(sprite.get_height() * scale_factor))
            sprite = pygame.transform.scale(sprite, scaled_size)

            # Use attack angle during attack, movement angle otherwise
            angle_to_use = self.attack_angle if self.is_attacking else self.movement_angle

            # Convert angle from radians to degrees for rotation
            rotation_angle = math.degrees(-angle_to_use)

            # Rotate the zombie sprite
            rotated_sprite = pygame.transform.rotate(sprite, rotation_angle)

            # Calculate position to center the rotated sprite on the zombie
            sprite_x = center_x - rotated_sprite.get_width() // 2
            sprite_y = center_y - rotated_sprite.get_height() // 2

            # Apply transparency if on object
            if self.is_on_object:
                # Create a copy with alpha for transparency effect
                rotated_sprite_copy = rotated_sprite.copy()
                rotated_sprite_copy.set_alpha(180)  # Semi-transparent
                screen.blit(rotated_sprite_copy, (sprite_x, sprite_y))
            else:
                # Optional: slight visual feedback for movement
                if self.is_moving and not self.is_attacking:
                    # Very subtle "wobble" effect during movement (slower for tough zombie)
                    wobble_offset = int(4 * abs(math.sin(self.animation_time * 3)))
                    sprite_x += wobble_offset

                # Add attack animation
                if self.is_attacking:
                    # Scale up even more during attack
                    scale = 1.3
                    attack_sprite = pygame.transform.scale(rotated_sprite,
                                                           (int(rotated_sprite.get_width() * scale),
                                                            int(rotated_sprite.get_height() * scale)))
                    # Center the scaled sprite
                    attack_sprite_x = center_x - attack_sprite.get_width() // 2
                    attack_sprite_y = center_y - attack_sprite.get_height() // 2
                    screen.blit(attack_sprite, (attack_sprite_x, attack_sprite_y))
                else:
                    screen.blit(rotated_sprite, (sprite_x, sprite_y))
        else:
            if self.is_on_object:
                # Create a transparent surface for the zombie when on an object
                circle_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
                # Draw a semi-transparent circle (128 is 50% opacity)
                pygame.draw.circle(circle_surface, (*self.color, 128), (self.width // 2, self.height // 2),
                                   self.width // 2)
                # Blit the surface to the screen
                screen.blit(circle_surface, (center_x - self.width // 2, center_y - self.height // 2))
            else:
                # Draw zombie normally when not on an object
                pygame.draw.circle(screen, self.color, (center_x, center_y), self.width // 2)

    def _apply_zombie_tint(self, sprite):
        """Apply red tint to tough zombie sprite

        Args:
            sprite (pygame.Surface): Original sprite

        Returns:
            pygame.Surface: Red-tinted sprite
        """
        # Create a copy of the sprite
        tinted_sprite = sprite.copy()

        # Create a red overlay
        red_overlay = pygame.Surface(sprite.get_size(), pygame.SRCALPHA)
        red_overlay.fill((255, 100, 100, 128))  # Semi-transparent red

        # Blend the overlay with the sprite
        tinted_sprite.blit(red_overlay, (0, 0), special_flags=pygame.BLEND_MULT)

        return tinted_sprite

    def get_score_value(self):
        """Get the score value for killing this zombie type

        Returns:
            int: Score value
        """
        return TOUGH_ZOMBIE_SCORE


class FastZombie(Zombie):
    """Fast zombie entity that is small and very quick"""

    def __init__(self, x, y):
        """Initialize the fast zombie

        Args:
            x (float): Initial x position
            y (float): Initial y position
        """
        # Call parent constructor with smaller size
        super().__init__(x, y)

        # Override size for fast zombie (smaller)
        self.width = FAST_ZOMBIE_SIZE
        self.height = FAST_ZOMBIE_SIZE
        self.rect = pygame.Rect(x, y, self.width, self.height)

        # Override properties for fast zombie
        self.color = BLUE  # Blue color for fast zombies
        # Random speed for fast zombies (much faster range)
        self.speed = random.uniform(FAST_ZOMBIE_SPEED_MIN, FAST_ZOMBIE_SPEED_MAX)
        self.health = FAST_ZOMBIE_HEALTH

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
                # Store the attack angle (direction towards player when attack starts)
                self.attack_angle = math.atan2(dy, dx)

                # Start attack animation
                self.is_attacking = True
                self.attack_animation_timer = ZOMBIE_ATTACK_DURATION

                # Reset attack timer (faster attack rate)
                self.attack_timer = ZOMBIE_ATTACK_COOLDOWN * 0.7  # 30% faster attacks

                # Play zombie attack sound
                from systems.audio import music_manager
                music_manager.play_sound("zombies_zombie_attack")

                # Deal damage to player (less damage than regular zombie)
                if player.take_damage(FAST_ZOMBIE_DAMAGE):
                    return True

        return False

    def render(self, screen, camera_offset=(0, 0)):
        """Render the fast zombie with smaller size

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

        # Get zombie sprite from texture atlas - use stand sprite during attack, hold sprite otherwise
        sprite_name = 'zoimbie1_stand' if self.is_attacking else 'zoimbie1_hold'
        from utils.sprite_loader import get_texture
        sprite = get_texture('zombie', sprite_name)
        if not sprite:
            # Fallback to old sprite system
            from utils.sprite_loader import get_sprite
            sprite = get_sprite('zombie_runner_1')

        if sprite:
            # Apply blue tint for fast zombie
            sprite = self._apply_zombie_tint(sprite)

            # Scale down sprite for fast zombie
            scaled_size = (int(sprite.get_width() * 0.7), int(sprite.get_height() * 0.7))
            sprite = pygame.transform.scale(sprite, scaled_size)

            # Use attack angle during attack, movement angle otherwise
            angle_to_use = self.attack_angle if self.is_attacking else self.movement_angle

            # Convert angle from radians to degrees for rotation
            rotation_angle = math.degrees(-angle_to_use)

            # Rotate the zombie sprite
            rotated_sprite = pygame.transform.rotate(sprite, rotation_angle)

            # Calculate position to center the rotated sprite on the zombie
            sprite_x = center_x - rotated_sprite.get_width() // 2
            sprite_y = center_y - rotated_sprite.get_height() // 2

            # Apply transparency if on object
            if self.is_on_object:
                # Create a copy with alpha for transparency effect
                rotated_sprite_copy = rotated_sprite.copy()
                rotated_sprite_copy.set_alpha(180)  # Semi-transparent
                screen.blit(rotated_sprite_copy, (sprite_x, sprite_y))
            else:
                # Optional: slight visual feedback for movement
                if self.is_moving and not self.is_attacking:
                    # Very subtle "wobble" effect during movement (faster for fast zombie)
                    wobble_offset = int(2 * abs(math.sin(self.animation_time * 8)))
                    sprite_x += wobble_offset

                # Add attack animation
                if self.is_attacking:
                    # Scale up slightly during attack but keep the same rotation
                    scale = 1.2
                    attack_sprite = pygame.transform.scale(rotated_sprite,
                                                           (int(rotated_sprite.get_width() * scale),
                                                            int(rotated_sprite.get_height() * scale)))
                    # Center the scaled sprite
                    attack_sprite_x = center_x - attack_sprite.get_width() // 2
                    attack_sprite_y = center_y - attack_sprite.get_height() // 2
                    screen.blit(attack_sprite, (attack_sprite_x, attack_sprite_y))
                else:
                    screen.blit(rotated_sprite, (sprite_x, sprite_y))
        else:
            # Fallback: draw circle if sprite not available
            if self.is_on_object:
                # Create a transparent surface for the zombie when on an object
                circle_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
                # Draw a semi-transparent circle (128 is 50% opacity)
                pygame.draw.circle(circle_surface, (*self.color, 128), (self.width // 2, self.height // 2),
                                   self.width // 2)
                # Blit the surface to the screen
                screen.blit(circle_surface, (center_x - self.width // 2, center_y - self.height // 2))
            else:
                # Draw zombie normally when not on an object
                pygame.draw.circle(screen, self.color, (center_x, center_y), self.width // 2)

    def _apply_zombie_tint(self, sprite):
        """Apply blue tint to fast zombie sprite

        Args:
            sprite (pygame.Surface): Original sprite

        Returns:
            pygame.Surface: Blue-tinted sprite
        """
        # Create a copy of the sprite
        tinted_sprite = sprite.copy()

        # Create a blue overlay
        blue_overlay = pygame.Surface(sprite.get_size(), pygame.SRCALPHA)
        blue_overlay.fill((100, 100, 255, 200))  # Semi-transparent blue

        # Blend the overlay with the sprite
        tinted_sprite.blit(blue_overlay, (0, 0), special_flags=pygame.BLEND_MULT)

        return tinted_sprite

    def get_score_value(self):
        """Get the score value for killing this zombie type

        Returns:
            int: Score value
        """
        return FAST_ZOMBIE_SCORE
