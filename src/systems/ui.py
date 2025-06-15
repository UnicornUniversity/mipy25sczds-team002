"""
UI System - Centralized UI Rendering
===================================

This module provides a centralized system for rendering UI elements in the game.
It includes classes and methods for rendering different UI elements, such as
the weapon inventory, pickup notifications, and debug information.
"""

import pygame
from utils.constants import (
    WINDOW_WIDTH, WINDOW_HEIGHT, DEBUG_FONT_SIZE, DEBUG_TEXT_COLOR,
    PLAYER_MAX_HEALTH, PICKUP_NOTIFICATION_DURATION
)

class UISystem:
    """
    Centralized system for rendering UI elements in the game.
    """

    def __init__(self):
        """Initialize the UI system."""
        # Create fonts
        self.debug_font = pygame.font.Font(None, DEBUG_FONT_SIZE)
        self.notification_font = pygame.font.Font(None, 36)
        self.inventory_font = pygame.font.Font(None, 24)
        
        # Pickup notification
        self.pickup_message = ""
        self.pickup_timer = 0
        
    def update(self, dt):
        """Update UI elements.
        
        Args:
            dt (float): Time delta in seconds
        """
        # Update pickup notification timer
        if self.pickup_timer > 0:
            self.pickup_timer -= dt
            
    def set_pickup_message(self, message):
        """Set the pickup notification message.
        
        Args:
            message (str): Message to display
        """
        self.pickup_message = message
        self.pickup_timer = PICKUP_NOTIFICATION_DURATION
        
    def render_weapon_inventory(self, screen, player):
        """Render the weapon inventory UI.
        
        Args:
            screen (pygame.Surface): Screen to render on
            player: The player with the weapon inventory
        """
        # Define the position and size of the inventory UI
        ui_x = 10
        ui_y = screen.get_height() - 40
        slot_width = 100
        slot_height = 30
        padding = 5
        
        # Draw each weapon slot
        for i in range(len(player.weapons)):
            # Calculate slot position
            slot_x = ui_x + i * (slot_width + padding)
            slot_y = ui_y
            
            # Draw slot background (highlight current slot)
            if i == player.current_weapon_slot:
                slot_color = (200, 200, 0)  # Yellow for current slot
            else:
                slot_color = (100, 100, 100)  # Gray for other slots
                
            # Draw slot rectangle
            pygame.draw.rect(screen, slot_color, (slot_x, slot_y, slot_width, slot_height))
            pygame.draw.rect(screen, (0, 0, 0), (slot_x, slot_y, slot_width, slot_height), 2)  # Black border
            
            # Draw weapon name if slot is not empty
            if player.weapons[i] is not None:
                # Get weapon name
                weapon_name = player.weapons[i].name
                
                # Render weapon name
                text = self.inventory_font.render(f"{i+1}: {weapon_name}", True, (0, 0, 0))
                
                # Center text in slot
                text_x = slot_x + (slot_width - text.get_width()) // 2
                text_y = slot_y + (slot_height - text.get_height()) // 2
                
                # Draw text
                screen.blit(text, (text_x, text_y))
            else:
                # Draw empty slot text
                text = self.inventory_font.render(f"{i+1}: Empty", True, (0, 0, 0))
                
                # Center text in slot
                text_x = slot_x + (slot_width - text.get_width()) // 2
                text_y = slot_y + (slot_height - text.get_height()) // 2
                
                # Draw text
                screen.blit(text, (text_x, text_y))
                
    def render_pickup_notification(self, screen):
        """Render the pickup notification.
        
        Args:
            screen (pygame.Surface): Screen to render on
        """
        if self.pickup_timer > 0:
            # Render the notification text
            notification_text = self.notification_font.render(self.pickup_message, True, (255, 255, 255))
            
            # Position the notification at the top center of the screen
            text_rect = notification_text.get_rect(center=(WINDOW_WIDTH // 2, 50))
            
            # Draw the notification
            screen.blit(notification_text, text_rect)
            
    def render_debug_info(self, screen, fps, player, enemy_system, items, bullets, effects, music_status):
        """Render debug information.
        
        Args:
            screen (pygame.Surface): Screen to render on
            fps (float): Current FPS
            player: The player
            enemy_system: The enemy system
            items (list): List of items
            bullets (list): List of bullets
            effects (list): List of effects
            music_status (dict): Music status information
        """
        # Create debug text lines
        debug_lines = [
            f"FPS: {fps:.1f}",
            f"Player Health: {player.health}/{PLAYER_MAX_HEALTH}",
            f"Player Position: ({player.x:.1f}, {player.y:.1f})",
            f"Active Zombies: {len(enemy_system.get_zombies())}",
            f"Game Time: {enemy_system.game_time:.1f}s",
            f"Spawn Rate: {enemy_system.current_spawn_rate:.1f}s",
            f"Items: {len(items)}",
            f"Bullets: {len(bullets)}",
            f"Effects: {len(effects)}",
            f"Current Weapon Slot: {player.current_weapon_slot + 1}",
            f"Current Weapon: {player.get_current_weapon().name if player.get_current_weapon() else 'None'}",
            f"Ammo: {player.get_current_weapon().ammo}/{player.get_current_weapon().magazine_size if player.get_current_weapon() else 0}",
            f"Reloading: {player.get_current_weapon().is_reloading if player.get_current_weapon() else False}",
            f"Weapon Inventory: {', '.join([w.name if w else 'Empty' for w in player.weapons])}",
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

# Global UI system instance
ui_system = UISystem()

def render_weapon_inventory(screen, player):
    """Convenience function to render the weapon inventory UI."""
    ui_system.render_weapon_inventory(screen, player)
    
def render_pickup_notification(screen):
    """Convenience function to render the pickup notification."""
    ui_system.render_pickup_notification(screen)
    
def render_debug_info(screen, fps, player, enemy_system, items, bullets, effects, music_status):
    """Convenience function to render debug information."""
    ui_system.render_debug_info(screen, fps, player, enemy_system, items, bullets, effects, music_status)
    
def set_pickup_message(message):
    """Convenience function to set the pickup notification message."""
    ui_system.set_pickup_message(message)
    
def update(dt):
    """Convenience function to update UI elements."""
    ui_system.update(dt)
