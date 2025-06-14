import pygame
import random
import math
from entities.player import Player
from entities.zombies import Zombie, ToughZombie
from entities.items import Item, HealthPack, Weapon, Powerup
from game.map_generator import MapGenerator
from utils.constants import (
    WINDOW_WIDTH, WINDOW_HEIGHT, TILE_SIZE,
    CAMERA_LERP, BLACK, WHITE, MAP_WIDTH, MAP_HEIGHT,
    DEBUG_FONT_SIZE, DEBUG_TEXT_COLOR,
    PLAYER_MAX_HEALTH, PICKUP_NOTIFICATION_DURATION
)


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

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                # Přepnout na gameplay
                return "gameplay"
        return None

    def render(self, screen, fps=0):
        screen_rect = screen.get_rect()
        title_rect = self.title_text.get_rect(center=(screen_rect.centerx, screen_rect.centery - 50))
        subtitle_rect = self.subtitle_text.get_rect(center=(screen_rect.centerx, screen_rect.centery + 50))

        screen.blit(self.title_text, title_rect)
        screen.blit(self.subtitle_text, subtitle_rect)


class GameplayState(GameState):
    """Main gameplay state"""

    def __init__(self):
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

        # Create a test item near the player
        self._spawn_test_item()

        # Create a list to store bullets
        self.bullets = []

        # Pickup notification
        self.pickup_message = ""
        self.pickup_timer = 0

        # Debug mode (toggled with F1)
        self.debug_mode = False
        self.debug_font = pygame.font.Font(None, DEBUG_FONT_SIZE)

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

    def _spawn_test_item(self):
        """Spawn a test item near the player"""
        # Find a position within 10 tiles of the player
        max_distance = 10 * TILE_SIZE

        # Try to find a walkable position for the item
        for _ in range(50):  # Limit attempts to avoid infinite loop
            # Random angle
            angle = random.uniform(0, 2 * 3.14159)
            # Random distance between 3 and 10 tiles
            distance = random.uniform(3 * TILE_SIZE, max_distance)

            # Calculate position
            x = self.player.x + distance * math.cos(angle)
            y = self.player.y + distance * math.sin(angle)

            # Ensure position is within map bounds
            x = max(0, min(x, MAP_WIDTH * TILE_SIZE - TILE_SIZE))
            y = max(0, min(y, MAP_HEIGHT * TILE_SIZE - TILE_SIZE))

            # Check if position is walkable
            if self.map_generator.is_walkable(x, y):
                # Create a random item at this position
                self.items.append(Item.create_random_item(x, y))
                break

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
        elif event.type == pygame.MOUSEMOTION:
            # Update player aim based on mouse position
            mouse_pos = pygame.mouse.get_pos()
            camera_offset = (int(self.camera_x), int(self.camera_y))
            self.player.update_aim(mouse_pos, camera_offset)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left mouse button
                # Attempt to shoot
                bullet = self.player.shoot()
                if bullet:
                    self.bullets.append(bullet)
        return None

    def update(self, dt):
        # Update player with map_generator reference
        self.player.update(dt, self.map_generator)

        # Update zombies with map_generator reference and check for collisions
        zombies_to_remove = []
        for i, zombie in enumerate(self.zombies):
            zombie.update(dt, self.player.x, self.player.y, self.map_generator)

            # Check for collision with player
            if self._check_collision(zombie, self.player):
                # Zombie attacks player
                zombie.attack(self.player)

                # Check if player is dead
                if self.player.is_dead():
                    # Handle game over (will be implemented later)
                    print("Game Over! Player died.")
                    # For now, just reset player health
                    self.player.health = 100

        # Update bullets and check for collisions
        bullets_to_remove = []
        for i, bullet in enumerate(self.bullets):
            # Update bullet position
            bullet.update(dt, self.map_generator)

            # Check if bullet has expired
            if bullet.is_expired():
                bullets_to_remove.append(i)
                continue

            # Check for collision with zombies
            for j, zombie in enumerate(self.zombies):
                if self._check_collision(bullet, zombie):
                    # Bullet hit zombie
                    zombie_died = zombie.take_damage(bullet.damage)

                    # Mark bullet for removal
                    bullets_to_remove.append(i)
                    break

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

    def _render_debug_info(self, screen, fps):
        """Render debug information on the screen"""
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
            f"Weapon: {self.player.weapon.name if self.player.weapon else 'None'}",
            f"Ammo: {self.player.weapon.ammo}/{self.player.weapon.magazine_size if self.player.weapon else 0}",
            f"Reloading: {self.player.weapon.is_reloading if self.player.weapon else False}",
            f"Pickup Message: {self.pickup_message if self.pickup_timer > 0 else 'None'}"
        ]

        # Render each line of debug text
        y_offset = 10
        for line in debug_lines:
            debug_text = self.debug_font.render(line, True, DEBUG_TEXT_COLOR)
            screen.blit(debug_text, (10, y_offset))
            y_offset += DEBUG_FONT_SIZE + 5  # Add some spacing between lines


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
