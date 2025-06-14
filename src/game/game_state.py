import pygame
import random
import math
from entities.player import Player
from entities.zombies import Zombie, ToughZombie
from entities.items import Item, HealthPack, Weapon, Powerup
from game.map_generator import MapGenerator
from systems.audio import play_menu_music, play_gameplay_music, stop_music, toggle_music, toggle_sfx, set_music_volume, set_sfx_volume
from utils.constants import (
    WINDOW_WIDTH, WINDOW_HEIGHT, TILE_SIZE,
    CAMERA_LERP, BLACK, WHITE, MAP_WIDTH, MAP_HEIGHT,
    DEBUG_FONT_SIZE, DEBUG_TEXT_COLOR,
    PLAYER_MAX_HEALTH, PICKUP_NOTIFICATION_DURATION,
    ZOMBIE_COLLISION_RADIUS
)
from utils.sprite_loader import get_asset_info


# Simple effect classes to replace missing systems.effects
class MuzzleFlash:
    """Simple muzzle flash effect"""
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.lifetime = 0.1  # Very short flash
        self.age = 0

    def update(self, dt):
        self.age += dt
        return self.age < self.lifetime

    def render(self, screen, camera_offset):
        if self.age < self.lifetime:
            # Simple yellow circle for muzzle flash
            screen_x = int(self.x - camera_offset[0])
            screen_y = int(self.y - camera_offset[1])
            radius = int(8 * (1 - self.age / self.lifetime))  # Shrinking
            if radius > 0:
                pygame.draw.circle(screen, (255, 255, 0), (screen_x, screen_y), radius)


class BulletImpact:
    """Simple bullet impact effect"""
    def __init__(self, x, y, color=(255, 255, 255)):
        self.x = x
        self.y = y
        self.color = color
        self.lifetime = 0.2
        self.age = 0

    def update(self, dt):
        self.age += dt
        return self.age < self.lifetime

    def render(self, screen, camera_offset):
        if self.age < self.lifetime:
            # Simple spark effect
            screen_x = int(self.x - camera_offset[0])
            screen_y = int(self.y - camera_offset[1])
            alpha = int(255 * (1 - self.age / self.lifetime))
            color_with_alpha = (*self.color, alpha)

            # Draw small cross for impact
            pygame.draw.line(screen, self.color, (screen_x-3, screen_y), (screen_x+3, screen_y), 2)
            pygame.draw.line(screen, self.color, (screen_x, screen_y-3), (screen_x, screen_y+3), 2)


class BloodSplatter:
    """Simple blood splatter effect"""
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.lifetime = 0.5
        self.age = 0

    def update(self, dt):
        self.age += dt
        return self.age < self.lifetime

    def render(self, screen, camera_offset):
        if self.age < self.lifetime:
            # Simple red circle for blood
            screen_x = int(self.x - camera_offset[0])
            screen_y = int(self.y - camera_offset[1])
            alpha = int(255 * (1 - self.age / self.lifetime))
            radius = int(4 + 2 * (self.age / self.lifetime))  # Growing

            # Create surface with alpha for transparency
            blood_surface = pygame.Surface((radius*2, radius*2), pygame.SRCALPHA)
            pygame.draw.circle(blood_surface, (150, 0, 0, alpha), (radius, radius), radius)
            screen.blit(blood_surface, (screen_x - radius, screen_y - radius))


class GameState:
    """Base class for game states"""

    def handle_event(self, event):
        """Event processing"""
        pass

    def update(self, dt):
        """State update"""
        pass

    def render(self, screen, fps=0):
        """State rendering"""
        pass


class MenuState(GameState):
    """Main menu"""

    def __init__(self):
        self.font = pygame.font.Font(None, 74)
        self.title_text = self.font.render("DEADLOCK", True, (255, 255, 255))
        self.subtitle_font = pygame.font.Font(None, 36)
        self.subtitle_text = self.subtitle_font.render("Press SPACE to start", True, (200, 200, 200))
        
        # Music controls info
        self.info_font = pygame.font.Font(None, 24)
        self.music_info = [
            "Music Controls:",
            "M - Toggle Music",
            "N - Toggle Sound Effects",
            "[ - Decrease Music Volume",
            "] - Increase Music Volume"
        ]
        
        self.music_started = False

    def update(self, dt):
        """Start menu music when first updated"""
        if not self.music_started:
            play_menu_music()
            self.music_started = True

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                # Přepnout na gameplay
                return "gameplay"
            elif event.key == pygame.K_m:
                # Toggle music
                toggle_music()
            elif event.key == pygame.K_n:
                # Toggle sound effects
                toggle_sfx()
            elif event.key == pygame.K_LEFTBRACKET:
                # Decrease music volume
                from systems.audio import music_manager
                current_volume = music_manager.music_volume
                set_music_volume(max(0.0, current_volume - 0.1))
            elif event.key == pygame.K_RIGHTBRACKET:
                # Increase music volume
                from systems.audio import music_manager
                current_volume = music_manager.music_volume
                set_music_volume(min(1.0, current_volume + 0.1))
        return None

    def render(self, screen, fps=0):
        screen_rect = screen.get_rect()
        title_rect = self.title_text.get_rect(center=(screen_rect.centerx, screen_rect.centery - 100))
        subtitle_rect = self.subtitle_text.get_rect(center=(screen_rect.centerx, screen_rect.centery - 20))

        screen.blit(self.title_text, title_rect)
        screen.blit(self.subtitle_text, subtitle_rect)
        
        # Render music controls info
        y_offset = screen_rect.centery + 50
        for line in self.music_info:
            info_text = self.info_font.render(line, True, (150, 150, 150))
            info_rect = info_text.get_rect(center=(screen_rect.centerx, y_offset))
            screen.blit(info_text, info_rect)
            y_offset += 30
        
        # Show current music status
        from systems.audio import music_manager
        status_lines = [
            f"Music: {'ON' if music_manager.music_enabled else 'OFF'}",
            f"Music Volume: {int(music_manager.music_volume * 100)}%",
            f"SFX Volume: {int(music_manager.sfx_volume * 100)}%"
        ]
        
        y_offset += 20
        for line in status_lines:
            status_text = self.info_font.render(line, True, (100, 255, 100))
            status_rect = status_text.get_rect(center=(screen_rect.centerx, y_offset))
            screen.blit(status_text, status_rect)
            y_offset += 25


class GameplayState(GameState):
    """Main gameplay state"""

    # Class variable to store the current instance
    instance = None

    def __init__(self):
        # Set the instance to self
        GameplayState.instance = self

        # Create the map generator
        self.map_generator = MapGenerator()

        # Find a walkable tile near the center for the player
        center_x = (TILE_SIZE * MAP_WIDTH) // 2
        center_y = (TILE_SIZE * MAP_HEIGHT) // 2

        # Search for a walkable tile in a spiral pattern around the center
        player_x, player_y = self._find_walkable_position(center_x, center_y)
        self.player = Player(player_x, player_y)

        # Camera position (top-left corner of the view)
        self.camera_x = 0
        self.camera_y = 0

        # Create a list to store zombies
        self.zombies = []

        # Create three test zombies at random positions away from the player
        for _ in range(3):
            self._spawn_zombie()

        # Create a list to store items
        self.items = []

        # Spawn random weapons around the map
        self._spawn_random_weapons(5)  # Spawn 5 random weapons

        # Create a list to store bullets
        self.bullets = []

        # Pickup notification
        self.pickup_message = ""
        self.pickup_timer = 0

        # Mouse button state tracking
        self.left_mouse_down = False

        # Debug mode (toggled with F1)
        self.debug_mode = False
        self.debug_font = pygame.font.Font(None, DEBUG_FONT_SIZE)

        # Visual effects
        self.effects = []
        
        # Music state
        self.gameplay_music_started = False

    def _find_walkable_position(self, center_x, center_y):
        """Find a walkable position near the specified center coordinates"""
        # Start at the center
        x, y = center_x, center_y

        # If the center is walkable, return it
        if self.map_generator.is_walkable(x, y):
            return x, y

        # Search in a spiral pattern
        for radius in range(1, 100):  # Limit search radius to avoid infinite loop
            # Check positions in a square around the center
            for dx in range(-radius, radius + 1):
                for dy in range(-radius, radius + 1):
                    # Skip positions that aren't on the edge of the square
                    if abs(dx) != radius and abs(dy) != radius:
                        continue

                    # Calculate position
                    pos_x = center_x + dx * TILE_SIZE
                    pos_y = center_y + dy * TILE_SIZE

                    # Check if position is walkable
                    if self.map_generator.is_walkable(pos_x, pos_y):
                        return pos_x, pos_y

        # If no walkable position found, return the center anyway
        return center_x, center_y

    def _spawn_zombie(self):
        """Spawn a zombie at a random position away from the player on a walkable tile"""
        # Choose a random position at least 200 pixels away from the player
        while True:
            x = random.randint(0, TILE_SIZE * MAP_WIDTH)
            y = random.randint(0, TILE_SIZE * MAP_HEIGHT)

            # Calculate distance to player
            dx = x - self.player.x
            dy = y - self.player.y
            distance = (dx * dx + dy * dy) ** 0.5

            # If far enough away and on a walkable tile, create the zombie
            if distance > 200 and self.map_generator.is_walkable(x, y):
                # 20% chance to spawn a tough zombie
                if random.random() < 0.2:
                    self.zombies.append(ToughZombie(x, y))
                else:
                    self.zombies.append(Zombie(x, y))
                break

    def _spawn_random_weapons(self, count=5):
        """Spawn random weapons around the map

        Args:
            count (int): Number of weapons to spawn
        """
        # Spawn the specified number of weapons
        for _ in range(count):
            # Find a random walkable position on the map
            self._spawn_random_item()

    def _spawn_random_item(self, near_player=False, weapon_type=None):
        """Spawn a random item at a random position on the map

        Args:
            near_player (bool): Whether to spawn the item near the player
            weapon_type (str, optional): Specific weapon type to spawn

        Returns:
            Item: The spawned item, or None if no suitable position was found
        """
        if near_player:
            # Find a position within 10 tiles of the player
            max_distance = 10 * TILE_SIZE
            min_distance = 3 * TILE_SIZE
            center_x = self.player.x
            center_y = self.player.y
        else:
            # Find a position anywhere on the map
            max_distance = min(MAP_WIDTH, MAP_HEIGHT) * TILE_SIZE / 2
            min_distance = 0
            # Use center of map as reference point
            center_x = (MAP_WIDTH * TILE_SIZE) / 2
            center_y = (MAP_HEIGHT * TILE_SIZE) / 2

        # Try to find a walkable position for the item
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
                # Create a random item at this position
                item = Item.create_random_item(x, y, weapon_type)
                self.items.append(item)
                return item

        return None

    def spawn_next_tier_weapon(self, current_weapon_type):
        """Spawn a weapon of the next tier based on the current weapon type

        Args:
            current_weapon_type (str): Current weapon type

        Returns:
            Item: The spawned weapon, or None if no suitable position was found or already at highest tier
        """
        # Get the next tier weapon type
        from entities.items import Weapon
        next_weapon_type = Weapon.get_next_tier_weapon(current_weapon_type)

        # If there is a next tier, spawn it near the player
        if next_weapon_type:
            return self._spawn_random_item(near_player=True, weapon_type=next_weapon_type)

        return None

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                return "menu"
            elif event.key == pygame.K_F1:
                # Toggle debug mode
                self.debug_mode = not self.debug_mode
            elif event.key == pygame.K_r:
                # Reload weapon
                if self.player.weapon:
                    self.player.weapon.reload()
            elif event.key == pygame.K_m:
                # Toggle music
                toggle_music()
            elif event.key == pygame.K_n:
                # Toggle sound effects
                toggle_sfx()
            elif event.key == pygame.K_LEFTBRACKET:
                # Decrease music volume
                from systems.audio import music_manager
                current_volume = music_manager.music_volume
                set_music_volume(max(0.0, current_volume - 0.1))
            elif event.key == pygame.K_RIGHTBRACKET:
                # Increase music volume
                from systems.audio import music_manager
                current_volume = music_manager.music_volume
                set_music_volume(min(1.0, current_volume + 0.1))
        elif event.type == pygame.MOUSEMOTION:
            # Update player aim based on mouse position
            mouse_pos = pygame.mouse.get_pos()
            camera_offset = (int(self.camera_x), int(self.camera_y))
            self.player.update_aim(mouse_pos, camera_offset)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left mouse button
                # Set flag for continuous firing
                self.left_mouse_down = True

                # Attempt to shoot immediately
                result = self.player.shoot()
                if result:
                    # Handle different return types from different weapons
                    if isinstance(result, list):
                        # Shotgun returns a list of pellets
                        self.bullets.extend(result)
                    else:
                        # Other weapons return a single bullet
                        self.bullets.append(result)

                    # Add muzzle flash effect
                    self._add_muzzle_flash_effect()
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:  # Left mouse button
                # Clear flag when button is released
                self.left_mouse_down = False
        return None

    def update(self, dt):
        # Start gameplay music when first updated
        if not self.gameplay_music_started:
            play_gameplay_music()
            self.gameplay_music_started = True
            
        # Update player with map_generator reference
        self.player.update(dt, self.map_generator)

        # Handle continuous firing for assault rifle
        if self.left_mouse_down and self.player.weapon and hasattr(self.player.weapon, 'name') and self.player.weapon.name == "Assault Rifle":
            result = self.player.shoot()
            if result:
                # Handle different return types from different weapons
                if isinstance(result, list):
                    # Shotgun returns a list of pellets
                    self.bullets.extend(result)
                else:
                    # Other weapons return a single bullet
                    self.bullets.append(result)

                # Add muzzle flash effect
                self._add_muzzle_flash_effect()

        # Update zombies with map_generator reference and check for collisions
        zombies_to_remove = []
        for i, zombie in enumerate(self.zombies):
            zombie.update(dt, self.player.x, self.player.y, self.map_generator)

            # Check for zombie-zombie collisions
            for j, other_zombie in enumerate(self.zombies):
                if i != j:  # Don't check collision with self
                    # Calculate distance between zombie centers
                    dx = (zombie.x + zombie.width/2) - (other_zombie.x + other_zombie.width/2)
                    dy = (zombie.y + zombie.height/2) - (other_zombie.y + other_zombie.height/2)
                    distance = math.sqrt(dx * dx + dy * dy)
                    
                    # If zombies are too close, push them apart
                    min_distance = ZOMBIE_COLLISION_RADIUS * 2
                    if distance < min_distance:
                        # Calculate push direction and force
                        if distance > 0:  # Avoid division by zero
                            push_x = dx / distance
                            push_y = dy / distance
                            push_force = (min_distance - distance) * 0.5
                            
                            # Move zombies apart
                            zombie.x += push_x * push_force
                            zombie.y += push_y * push_force
                            other_zombie.x -= push_x * push_force
                            other_zombie.y -= push_y * push_force

            # Check for collision with player
            if self._check_collision(zombie, self.player):
                # Zombie attacks player
                zombie.attack(self.player)

                # Check if player is dead
                if self.player.is_dead():
                    # Handle game over
                    self._handle_game_over()
                    return  # Stop updating the game state

        # Update bullets and check for collisions
        bullets_to_remove = []
        for i, bullet in enumerate(self.bullets):
            # Update bullet position
            bullet.update(dt, self.map_generator)

            # Check if bullet has expired
            if bullet.is_expired():
                # Add bullet impact effect when bullet expires
                self._add_bullet_impact_effect(bullet.x, bullet.y, bullet.color)
                bullets_to_remove.append(i)
                continue

            # Check for collision with zombies
            for j, zombie in enumerate(self.zombies):
                if self._check_collision(bullet, zombie):
                    # Bullet hit zombie
                    zombie_died = zombie.take_damage(bullet.damage)

                    # Add blood splatter effect
                    self._add_blood_splatter_effect(zombie.x + zombie.width // 2, zombie.y + zombie.height // 2)

                    # Mark bullet for removal
                    bullets_to_remove.append(i)
                    break

            # Check for collision with map (walls)
            if not bullets_to_remove or i not in bullets_to_remove:
                if self.map_generator and not self.map_generator.is_walkable(bullet.x, bullet.y):
                    # Add bullet impact effect
                    self._add_bullet_impact_effect(bullet.x, bullet.y, bullet.color)

                    # Mark bullet for removal
                    bullets_to_remove.append(i)

        # Remove expired or collided bullets
        self.bullets = [b for i, b in enumerate(self.bullets) if i not in bullets_to_remove]

        # Remove dead zombies
        self.zombies = [zombie for zombie in self.zombies if not zombie.is_dead()]

        # Check for item pickups
        for item in self.items:
            if not item.picked_up and self._check_collision(item, self.player):
                # Item is picked up by player
                message = item.pickup(self.player)
                self.pickup_message = message
                self.pickup_timer = PICKUP_NOTIFICATION_DURATION

        # Update pickup notification timer
        if self.pickup_timer > 0:
            self.pickup_timer -= dt

        # Update effects
        effects_to_remove = []
        for i, effect in enumerate(self.effects):
            # update() returns True if effect should continue, False if finished
            should_continue = effect.update(dt)
            if not should_continue:
                effects_to_remove.append(i)

        # Remove finished effects
        self.effects = [e for i, e in enumerate(self.effects) if i not in effects_to_remove]

        # Update camera position to follow player (with smoothing)
        target_camera_x = self.player.x - WINDOW_WIDTH // 2
        target_camera_y = self.player.y - WINDOW_HEIGHT // 2

        # Apply camera smoothing
        self.camera_x += (target_camera_x - self.camera_x) * CAMERA_LERP
        self.camera_y += (target_camera_y - self.camera_y) * CAMERA_LERP

        # Calculate map boundaries in pixels
        map_width_px = MAP_WIDTH * TILE_SIZE
        map_height_px = MAP_HEIGHT * TILE_SIZE

        # Constrain camera to map boundaries
        # Left boundary
        if self.camera_x < 0:
            self.camera_x = 0
        # Right boundary (map width - screen width)
        elif self.camera_x > map_width_px - WINDOW_WIDTH:
            self.camera_x = map_width_px - WINDOW_WIDTH

        # Top boundary
        if self.camera_y < 0:
            self.camera_y = 0
        # Bottom boundary (map height - screen height)
        elif self.camera_y > map_height_px - WINDOW_HEIGHT:
            self.camera_y = map_height_px - WINDOW_HEIGHT

    def render(self, screen, fps=0):
        # Calculate camera offset for rendering
        camera_offset = (int(self.camera_x), int(self.camera_y))

        # Draw the map with camera offset
        self.map_generator.render(screen, camera_offset)

        # Draw items with camera offset
        for item in self.items:
            item.render(screen, camera_offset)

        # Draw bullets with camera offset
        for bullet in self.bullets:
            bullet.render(screen, camera_offset)

        # Draw zombies with camera offset
        for zombie in self.zombies:
            zombie.render(screen, camera_offset)

        # Draw player with camera offset
        self.player.render(screen, camera_offset)

        # Draw effects with camera offset
        for effect in self.effects:
            effect.render(screen, camera_offset)

        # Draw pickup notification if active
        if self.pickup_timer > 0:
            # Create a font for the notification
            notification_font = pygame.font.Font(None, 36)

            # Render the notification text
            notification_text = notification_font.render(self.pickup_message, True, WHITE)

            # Position the notification at the top center of the screen
            text_rect = notification_text.get_rect(center=(WINDOW_WIDTH // 2, 50))

            # Draw the notification
            screen.blit(notification_text, text_rect)

        # Render debug information if debug mode is enabled
        if self.debug_mode:
            self._render_debug_info(screen, fps)

    def _check_collision(self, entity1, entity2):
        """Check if two entities are colliding

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

        # Check if distance is less than sum of radii (using width as diameter)
        return distance < (entity1.width + entity2.width) / 2

    def _add_muzzle_flash_effect(self):
        """Add a muzzle flash effect at the player's weapon position"""
        if not self.player.weapon:
            return

        # Calculate muzzle position (slightly in front of player in aim direction)
        spawn_distance = self.player.width // 2 + 5  # 5 pixels in front of player edge
        muzzle_x = self.player.x + self.player.width // 2 + math.cos(self.player.aim_angle) * spawn_distance
        muzzle_y = self.player.y + self.player.height // 2 + math.sin(self.player.aim_angle) * spawn_distance

        # Create muzzle flash effect
        flash = MuzzleFlash(muzzle_x, muzzle_y)
        self.effects.append(flash)

    def _add_bullet_impact_effect(self, x, y, color=None):
        """Add a bullet impact effect at the specified position

        Args:
            x (float): X position
            y (float): Y position
            color (tuple, optional): Color of the impact
        """
        # Use bullet color if provided, otherwise use white
        impact_color = color or (255, 255, 255)

        # Create bullet impact effect
        impact = BulletImpact(x, y, impact_color)
        self.effects.append(impact)

    def _add_blood_splatter_effect(self, x, y):
        """Add a blood splatter effect at the specified position

        Args:
            x (float): X position
            y (float): Y position
        """
        # Create blood splatter effect
        splatter = BloodSplatter(x, y)
        self.effects.append(splatter)

    def _render_debug_info(self, screen, fps):
        """Render debug information on the screen"""
        # Get music status for debug info
        from systems.audio import music_manager
        music_status = music_manager.get_status()
        
        # Create debug text lines
        debug_lines = [
            f"FPS: {fps:.1f}",
            f"Player Health: {self.player.health}/{PLAYER_MAX_HEALTH}",
            f"Player Position: ({self.player.x:.1f}, {self.player.y:.1f})",
            f"Tile Position: ({int(self.player.x // TILE_SIZE)}, {int(self.player.y // TILE_SIZE)})",
            f"On Object: {self.player.is_on_object}",
            f"Speed Multiplier: {self.player.debug_speed_multiplier:.1f}",
            f"Zombies: {len(self.zombies)}",
            f"Items: {len(self.items)}",
            f"Bullets: {len(self.bullets)}",
            f"Effects: {len(self.effects)}",
            f"Weapon: {self.player.weapon.name if self.player.weapon else 'None'}",
            f"Ammo: {self.player.weapon.ammo}/{self.player.weapon.magazine_size if self.player.weapon else 0}",
            f"Reloading: {self.player.weapon.is_reloading if self.player.weapon else False}",
            f"Pickup Message: {self.pickup_message if self.pickup_timer > 0 else 'None'}",
            f"Music: {music_status['current_track'] or 'None'} ({music_status['current_category'] or 'None'})",
            f"Music Volume: {int(music_status['music_volume'] * 100)}%",
            f"Music Enabled: {music_status['music_enabled']}"
        ]

        # Render each line of debug text
        y_offset = 10
        for line in debug_lines:
            debug_text = self.debug_font.render(line, True, DEBUG_TEXT_COLOR)
            screen.blit(debug_text, (10, y_offset))
            y_offset += DEBUG_FONT_SIZE + 5  # Add some spacing between lines

    def _handle_game_over(self):
        """Handle game over state"""
        # Clear all zombies and bullets
        self.zombies.clear()
        self.bullets.clear()
        
        # Reset player health
        self.player.health = PLAYER_MAX_HEALTH
        
        # Reset player position to center of map
        center_x = (TILE_SIZE * MAP_WIDTH) // 2
        center_y = (TILE_SIZE * MAP_HEIGHT) // 2
        player_x, player_y = self._find_walkable_position(center_x, center_y)
        self.player.x = player_x
        self.player.y = player_y
        
        # Spawn new zombies
        for _ in range(3):
            self._spawn_zombie()
            
        # Add game over message
        self.pickup_message = "Game Over! You died and respawned."
        self.pickup_timer = PICKUP_NOTIFICATION_DURATION


class GameStateManager:
    """Game state manager"""

    def __init__(self):
        self.states = {
            "menu": MenuState(),
            "gameplay": GameplayState()
        }
        self.current_state = "menu"

    def handle_event(self, event):
        new_state = self.states[self.current_state].handle_event(event)
        if new_state and new_state in self.states:
            self.current_state = new_state

    def update(self, dt):
        self.states[self.current_state].update(dt)

    def render(self, screen, fps=0):
        self.states[self.current_state].render(screen, fps)
