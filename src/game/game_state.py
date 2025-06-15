"""
Game State Management System
===========================

Manages different game states like menu, gameplay, pause, game over.
Refactored to use proper collision system and animation system.
"""

import pygame
import math
from abc import ABC, abstractmethod

from entities.zombies import FastZombie
from systems import collisions
from utils.constants import *
from systems.audio import music_manager
from systems.collisions import check_entity_collision, initialize as collision_init
from systems.enemy_spawner import EnemySpawner
from systems.item_spawner import ItemSpawner
from systems.animation import animation_system  # Import global animation system
from entities.player import Player
from game.map_generator import MapGenerator


class GameState(ABC):
    """Abstract base class for all game states"""

    @abstractmethod
    def update(self, dt):
        """Update state logic"""
        pass

    @abstractmethod
    def handle_event(self, event):
        """Handle pygame events"""
        pass

    @abstractmethod
    def render(self, screen, fps=0):
        """Render state"""
        pass


class MenuState(GameState):
    """Main menu state"""

    def __init__(self):
        """Initialize menu state"""
        self.font = pygame.font.Font(None, 74)
        self.title_text = self.font.render("DEADLOCK", True, WHITE)

        self.subtitle_font = pygame.font.Font(None, 36)
        self.subtitle_text = self.subtitle_font.render("Press SPACE to Start", True, WHITE)

        self.info_font = pygame.font.Font(None, 24)

        # Music info
        self.music_info = "Loading music..."
        self.music_started = False

    def update(self, dt):
        """Update menu state"""
        # Start menu music
        if not self.music_started:
            music_manager.play_music("menu_music")
            self.music_started = True

    def handle_event(self, event):
        """Handle menu events"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                # Stop menu music before switching to gameplay
                music_manager.stop_music()
                return "gameplay"

            elif event.key == pygame.K_m:
                # Toggle music
                if music_manager.is_playing():
                    music_manager.stop_music()
                else:
                    music_manager.play_music("menu_music")

            elif event.key == pygame.K_PLUS or event.key == pygame.K_EQUALS:
                # Increase volume
                music_manager.set_volume(min(1.0, music_manager.get_volume() + 0.1))

            elif event.key == pygame.K_MINUS:
                # Decrease volume
                music_manager.set_volume(max(0.0, music_manager.get_volume() - 0.1))

        return None

    def render(self, screen, fps=0):
        """Render menu"""
        screen.fill(BLACK)

        # Title
        title_rect = self.title_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 100))
        screen.blit(self.title_text, title_rect)

        # Subtitle
        subtitle_rect = self.subtitle_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2))
        screen.blit(self.subtitle_text, subtitle_rect)

        # Controls
        controls = [
            "Controls:",
            "Left Click - Shoot",
            "R - Reload",
            "1-5 - Switch Weapons",
            "",
            "M - Toggle Music",
            "+/- - Volume Control",
        ]

        y_offset = WINDOW_HEIGHT // 2 + 80
        for line in controls:
            if line:  # Skip empty lines for spacing
                text = self.info_font.render(line, True, WHITE)
                text_rect = text.get_rect(center=(WINDOW_WIDTH // 2, y_offset))
                screen.blit(text, text_rect)
            y_offset += 25

        # Music info
        music_text = self.info_font.render(self.music_info, True, YELLOW)
        music_rect = music_text.get_rect(bottomright=(WINDOW_WIDTH - 10, WINDOW_HEIGHT - 10))
        screen.blit(music_text, music_rect)

        # FPS counter
        fps_text = self.info_font.render(f"FPS: {int(fps)}", True, WHITE)
        screen.blit(fps_text, (10, 10))


class GameplayState(GameState):
    """Main gameplay state with proper collision and animation systems"""

    def __init__(self):
        """Initialize gameplay state"""
        # Add GameUI system
        from systems.ui import GameUI
        self.ui = GameUI()

        # Game entities - center player on map
        map_center_x = (MAP_WIDTH * TILE_SIZE) // 2
        map_center_y = (MAP_HEIGHT * TILE_SIZE) // 2
        self.player = Player(map_center_x, map_center_y)

        # Game systems
        self.map_generator = MapGenerator()

        # Initialize collision system with map generator
        collision_init(self.map_generator)

        self.enemy_system = EnemySpawner(self.map_generator)
        self.item_spawner = ItemSpawner(self.map_generator)
        self.item_spawner.ui = self.ui  # Connect UI for pickup notifications
        self.bullets = []

        self.camera_y = 0

        # Game state
        self.paused = False
        self.score = 0

        # Debug flags
        self.show_debug = False

        # Music
        self.music_started = False

    def update(self, dt):
        """Update gameplay state"""
        if self.paused:
            return

            # Update UI system
        self.ui.update(dt)

        # Start gameplay music
        if not self.music_started:
            music_manager.play_music("gameplay_music")
            self.music_started = True

        # Check if left mouse button is held down for continuous firing
        if pygame.mouse.get_pressed()[0]:  # Left mouse button
            # Get current weapon to check if it's an assault rifle
            current_weapon = self.player.get_current_weapon()
            if current_weapon and current_weapon.name == "Assault Rifle":
                self._handle_player_shoot()

        self.player.update(dt, self.map_generator)
        self.enemy_system.update(dt, self.player.x, self.player.y)
        self.item_spawner.update(dt)

        animation_system.update(dt)

        self._handle_bullet_update(dt)
        self._update_camera()
        self._check_collisions()

    def handle_event(self, event):
        """Handle gameplay events"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                return "pause"
            elif event.key == pygame.K_r:
                self.player.reload()
            elif event.key == pygame.K_q:
                self.player.cycle_weapons_backward()
            elif event.key == pygame.K_e:
                self.player.cycle_weapons_forward()
            elif event.key in [pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4, pygame.K_5]:
                slot = event.key - pygame.K_1
                self.player.switch_weapon(slot)
            elif event.key == pygame.K_F2:
                self._spawn_all_item_types()  # Debug: Spawn all item types in front of player
            elif event.key == pygame.K_F3:
                self.show_debug = not self.show_debug
            elif event.key == pygame.K_F4:
                self._spawn_debug_zombie()  # Debug: Spawn zombie near player


        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click
                self._handle_player_shoot()

        elif event.type == pygame.MOUSEMOTION:
            # Update player aim
            camera_offset = (self.camera_x, self.camera_y)
            self.player.update_aim(event.pos, camera_offset)

        return None

    def render(self, screen, fps=0):
        """Render gameplay"""
        screen.fill(BLACK)

        # Calculate camera offset
        camera_offset = (self.camera_x, self.camera_y)
        self.map_generator.render(screen, camera_offset)
        self.item_spawner.render(screen, camera_offset)
        self.player.render(screen, camera_offset)
        self.enemy_system.render(screen, camera_offset)

        for bullet in self.bullets:
            bullet.render(screen, camera_offset)

        animation_system.render(screen, camera_offset)

        self._render_ui(screen, fps)
        if self.show_debug:
            self._render_debug_info(screen, fps, camera_offset)

    def _update_camera(self):
        """Update camera to follow player"""
        # Center camera on player
        self.camera_x = self.player.x - WINDOW_WIDTH // 2
        self.camera_y = self.player.y - WINDOW_HEIGHT // 2

        # Clamp camera to map bounds
        map_width = MAP_WIDTH * TILE_SIZE
        map_height = MAP_HEIGHT * TILE_SIZE

        self.camera_x = max(0, min(self.camera_x, map_width - WINDOW_WIDTH))
        self.camera_y = max(0, min(self.camera_y, map_height - WINDOW_HEIGHT))

    def _handle_bullet_update(self, dt):
        for bullet in self.bullets[:]:  # Create copy to avoid modification during iteration
            bullet.update(dt, self.map_generator)

            # Check collision with zombies
            hit_zombie = None
            for zombie in self.enemy_system.zombies[:]:
                if collisions.check_entity_collision(bullet, zombie):
                    # Add blood effect when zombie is hit - USE ANIMATION SYSTEM
                    blood_x = zombie.x + zombie.width / 2
                    blood_y = zombie.y + zombie.height / 2
                    animation_system.add_effect('blood_splatter', blood_x, blood_y, 0.8)

                    if zombie.take_damage(bullet.damage):
                        self.enemy_system.zombies.remove(zombie)
                        # Use zombie-specific score value
                        self.score += zombie.get_score_value()
                    hit_zombie = zombie
                    break

            # Remove bullet if it hit something or expired
            if hit_zombie or bullet.is_expired():
                if bullet in self.bullets:
                    self.bullets.remove(bullet)

                # Handle explosive bullets hitting zombies
                if bullet.is_explosive and hit_zombie:
                    explosion_data = bullet.explode()
                    if explosion_data:
                        self._handle_explosion(explosion_data)

                # Handle explosive bullets hitting walls
                if bullet.is_explosive and bullet.hit_wall and bullet.wall_hit_explosion:
                    self._handle_explosion(bullet.wall_hit_explosion)

    def _handle_player_shoot(self):
        """Handle player shooting"""
        if pygame.mouse.get_pressed()[0]:  # Left mouse button
            projectiles = self.player.shoot()
            if projectiles:
                # Add muzzle flash animation
                self._add_muzzle_flash_animation()

                if isinstance(projectiles, list):
                    # Multiple projectiles (shotgun)
                    self.bullets.extend(projectiles)
                else:
                    # Single projectile
                    self.bullets.append(projectiles)

    def _add_muzzle_flash_animation(self):
        """Add muzzle flash animation at weapon position"""
        current_weapon = self.player.get_current_weapon()
        if current_weapon:
            # Get weapon muzzle position from weapon system
            player_center_x = self.player.x + self.player.width / 2
            player_center_y = self.player.y + self.player.height / 2
            muzzle_x, muzzle_y = current_weapon.get_muzzle_position(player_center_x, player_center_y,
                                                                    self.player.aim_angle)
        else:
            # Fallback to old calculation if no weapon
            muzzle_offset = 30
            player_center_x = self.player.x + self.player.width / 2
            player_center_y = self.player.y + self.player.height / 2
            muzzle_x = player_center_x + muzzle_offset * math.cos(self.player.aim_angle)
            muzzle_y = player_center_y + muzzle_offset * math.sin(self.player.aim_angle)

        # Add muzzle flash effect
        animation_system.add_effect('muzzle_flash', muzzle_x, muzzle_y, 0.1)

    def _simulate_projectile_hit(self, projectile):
        """Simulate projectile hit for demonstration"""
        # This is a simplified version - in full game, projectiles would travel
        hit_x = self.player.x + 100 * math.cos(self.player.aim_angle)
        hit_y = self.player.y + 100 * math.sin(self.player.aim_angle)

        # Check if we hit any zombies
        zombies = self.enemy_system.get_zombies()
        for zombie in zombies:
            distance = math.sqrt((zombie.x - hit_x) ** 2 + (zombie.y - hit_y) ** 2)
            if distance < 50:  # Hit radius
                # Add blood splatter animation
                animation_system.add_effect('blood_splatter', zombie.x, zombie.y, 1.0)

                # Damage zombie
                if zombie.take_damage(projectile.damage):
                    self.enemy_system.remove_zombie(zombie)
                    self.score += 10
                break
        else:
            # No zombie hit, add bullet impact
            animation_system.add_effect('bullet_impact', hit_x, hit_y, 0.3)

    def _spawn_debug_zombie(self):
        """Debug function to spawn a random zombie near the player"""
        import random
        from entities.zombies import Zombie, ToughZombie

        # Random choice between weak and tough zombie
        zombie_types = [
            ("weak", Zombie),
            ("tough", ToughZombie),
            ("fast", FastZombie)
        ]

        zombie_type_name, zombie_class = random.choice(zombie_types)

        # Calculate spawn position near player (but not too close)
        spawn_distance = 150  # Distance from player
        angle = random.uniform(0, 2 * math.pi)  # Random angle

        spawn_x = self.player.x + spawn_distance * math.cos(angle)
        spawn_y = self.player.y + spawn_distance * math.sin(angle)

        # Ensure spawn position is within map bounds
        map_width = MAP_WIDTH * TILE_SIZE
        map_height = MAP_HEIGHT * TILE_SIZE
        spawn_x = max(50, min(spawn_x, map_width - 50))
        spawn_y = max(50, min(spawn_y, map_height - 50))

        # Create and add the zombie
        new_zombie = zombie_class(spawn_x, spawn_y)
        self.enemy_system.zombies.append(new_zombie)

        # Show notification
        message = f"Spawned {zombie_type_name} zombie! (Total: {len(self.enemy_system.zombies)})"
        print(message)  # Console output

        # UI notification if available
        if self.ui:
            self.ui.show_info_message(message, 2.0)

        # Visual effect at spawn location
        from systems.animation import animation_system
        animation_system.add_effect('explosion', spawn_x, spawn_y, 0.3, size=0.3)

    def _check_collisions(self):
        """Check collisions between game entities using proper collision system"""
        zombies = self.enemy_system.get_zombies()

        # Check zombie-player collisions using entity collision detection
        for zombie in zombies:
            if check_entity_collision(self.player, zombie):
                if zombie.attack(self.player):
                    # Add blood splatter when player is hit
                    animation_system.add_effect('blood_splatter', self.player.x, self.player.y, 0.8)

                    if self.player.is_dead():
                        return "game_over"

        picked_items = self.item_spawner.check_pickups(self.player)
        for item in picked_items:
            animation_system.add_effect('explosion', item.x, item.y, 0.5, size=0.5)

    def _render_ui(self, screen, fps):
        """Render game UI using GameUI system"""
        # Use new GameUI system instead of manual UI rendering
        self.ui.render_hud(screen, self.player, self.score, fps)
        self.ui.render_notifications(screen)


    def _render_debug_info(self, screen, fps, camera_offset):
        """Render debug information"""
        font = pygame.font.Font(None, 20)
        debug_info = [
            f"Player: ({int(self.player.x)}, {int(self.player.y)})",
            f"Camera: ({int(camera_offset[0])}, {int(camera_offset[1])})",
            f"Zombies: {len(self.enemy_system.get_zombies())}",
            f"Active Animations: {len(animation_system.effects)}",
            f"Aim Angle: {math.degrees(self.player.aim_angle):.1f}°"
        ]

        y_offset = WINDOW_HEIGHT - len(debug_info) * 25 - 10
        for info in debug_info:
            text = font.render(info, True, YELLOW)
            screen.blit(text, (10, y_offset))
            y_offset += 25

    def _handle_explosion(self, explosion_data):
        """Handle explosive damage with visual effects"""
        explosion_x, explosion_y = explosion_data['position']
        explosion_radius = explosion_data['radius']
        explosion_damage = explosion_data['damage']

        # Add explosion visual effect
        animation_system.add_effect('explosion', explosion_x, explosion_y, 0.6, radius=explosion_radius)

        # Damage all zombies in explosion radius
        import math
        for zombie in self.enemy_system.zombies[:]:
            zombie_center_x = zombie.x + zombie.width / 2
            zombie_center_y = zombie.y + zombie.height / 2

            distance = math.sqrt((zombie_center_x - explosion_x) ** 2 + (zombie_center_y - explosion_y) ** 2)

            if distance <= explosion_radius:
                # Add blood effect for each hit zombie
                animation_system.add_effect('blood_splatter', zombie_center_x, zombie_center_y, 0.8)

                # Damage decreases with distance
                damage_multiplier = 1.0 - (distance / explosion_radius)
                actual_damage = int(explosion_damage * damage_multiplier)

                if zombie.take_damage(actual_damage):
                    self.enemy_system.zombies.remove(zombie)
                    # Use zombie-specific score value with bonus for explosive kills
                    self.score += zombie.get_score_value() + 5  # +5 bonus for explosive kills


    def _spawn_all_item_types(self):
        """Debug function to spawn all item types in front of the player"""
        from systems.items.item_factory import ItemFactory

        # Get all item types
        basic_items = ItemFactory.get_basic_item_types()
        powerup_types = ItemFactory.get_powerup_types()
        all_item_types = basic_items + powerup_types

        player_x, player_y = self.player.x, self.player.y
        aim_angle = self.player.aim_angle

        radius = 100  # Distance from player
        item_count = len(all_item_types)
        angle_step = math.pi / (item_count + 1)  # Distribute items in a semi-circle
        for i, item_type in enumerate(all_item_types):
            angle = aim_angle - math.pi/2 + angle_step * (i + 1)
            x = player_x + radius * math.cos(angle)
            y = player_y + radius * math.sin(angle)

            if item_type == "weapon":
                # Spawn one of each weapon type
                for weapon_type in ItemFactory._weapon_types:
                    weapon_angle = angle + (0.1 * (ItemFactory._weapon_types.index(weapon_type) - len(ItemFactory._weapon_types)/2))
                    weapon_x = player_x + (radius + 30) * math.cos(weapon_angle)
                    weapon_y = player_y + (radius + 30) * math.sin(weapon_angle)
                    self.item_spawner.spawn_weapon(weapon_type, (weapon_x, weapon_y))
            else:
                self.item_spawner.spawn_specific_item(item_type, (x, y))

        if self.ui:
            self.ui.show_info_message("Spawned all item types", 3.0)


class PauseState(GameState):
    """Pause menu state"""

    def __init__(self):
        """Initialize pause state"""
        self.font = pygame.font.Font(None, 74)
        self.title_text = self.font.render("PAUSED", True, WHITE)

        self.subtitle_font = pygame.font.Font(None, 36)
        self.subtitle_text = self.subtitle_font.render("Press ESC to Continue", True, WHITE)

    def update(self, dt):
        """Update pause state"""
        pass

    def handle_event(self, event):
        """Handle pause events"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                return "gameplay"
            elif event.key == pygame.K_m:
                return "menu"
        return None

    def render(self, screen, fps=0):
        """Render pause menu"""
        # Semi-transparent overlay
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        overlay.set_alpha(128)
        overlay.fill(BLACK)
        screen.blit(overlay, (0, 0))

        # Title
        title_rect = self.title_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 50))
        screen.blit(self.title_text, title_rect)

        # Subtitle
        subtitle_rect = self.subtitle_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 20))
        screen.blit(self.subtitle_text, subtitle_rect)


class GameOverState(GameState):
    """Game over state"""

    def __init__(self, score=0):
        """Initialize game over state"""
        self.score = score
        self.font = pygame.font.Font(None, 74)
        self.title_text = self.font.render("GAME OVER", True, RED)

        self.subtitle_font = pygame.font.Font(None, 36)
        self.score_text = self.subtitle_font.render(f"Score: {score}", True, WHITE)
        self.restart_text = self.subtitle_font.render("Press SPACE to Restart", True, WHITE)

    def update(self, dt):
        """Update game over state"""
        pass

    def handle_event(self, event):
        """Handle game over events"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                return "gameplay"
            elif event.key == pygame.K_ESCAPE:
                return "menu"
        return None

    def render(self, screen, fps=0):
        """Render game over screen"""
        screen.fill(BLACK)

        # Title
        title_rect = self.title_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 100))
        screen.blit(self.title_text, title_rect)

        # Score
        score_rect = self.score_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2))
        screen.blit(self.score_text, score_rect)

        # Restart instruction
        restart_rect = self.restart_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 50))
        screen.blit(self.restart_text, restart_rect)


class GameStateManager:
    """Manager for handling game state transitions"""

    def __init__(self):
        """Initialize game state manager"""
        self.states = {
            "menu": MenuState(),
            "gameplay": None,  # Will be created when needed
            "pause": None,  # Will be created when needed
            "game_over": None  # Will be created when needed
        }
        self.current_state = "menu"
        self.previous_state = None

    def handle_event(self, event):
        """Handle events and state transitions"""
        if self.current_state in self.states and self.states[self.current_state]:
            next_state = self.states[self.current_state].handle_event(event)
            if next_state:
                self._change_state(next_state)

    def update(self, dt):
        """Update current state"""
        if self.current_state in self.states and self.states[self.current_state]:
            self.states[self.current_state].update(dt)

    def render(self, screen, fps=0):
        """Render current state"""
        if self.current_state in self.states and self.states[self.current_state]:
            self.states[self.current_state].render(screen, fps)

    def _change_state(self, new_state):
        """Change to a new state"""
        self.previous_state = self.current_state
        self.current_state = new_state

        # Create state instances as needed
        if new_state == "gameplay":
            self.states["gameplay"] = GameplayState()
        elif new_state == "pause":
            self.states["pause"] = PauseState()
        elif new_state == "game_over":
            # Get score from gameplay state if available
            score = 0
            if self.states["gameplay"]:
                score = self.states["gameplay"].score
            self.states["game_over"] = GameOverState(score)
