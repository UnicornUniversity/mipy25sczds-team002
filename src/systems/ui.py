import pygame
from utils.constants import (
    WHITE, RED, GREEN, BLUE, BLACK, GRAY,
    PICKUP_NOTIFICATION_DURATION,
    WINDOW_WIDTH
)

class NotificationSystem:
    """System for displaying temporary text notifications"""
    
    def __init__(self, font_size=24):
        """Initialize notification system
        
        Args:
            font_size (int): Size of notification text
        """
        self.font = pygame.font.Font(None, font_size)
        self.notifications = []  # List of active notifications
        
    def add_notification(self, message, duration=PICKUP_NOTIFICATION_DURATION, 
                        color=WHITE, position="center"):
        """Add a new notification
        
        Args:
            message (str): Text to display
            duration (float): How long to show (seconds)
            color (tuple): RGB color for text
            position (str): "center", "top", "bottom", "top-left", etc.
        """
        notification = {
            'message': message,
            'timer': duration,
            'color': color,
            'position': position,
            'surface': self.font.render(message, True, color)
        }
        self.notifications.append(notification)
    
    def add_pickup_message(self, message):
        """Convenience method for pickup notifications"""
        self.add_notification(message, color=GREEN, position="center-bottom")
    
    def add_damage_message(self, message):
        """Convenience method for damage notifications"""
        self.add_notification(message, duration=1.5, color=RED, position="center")
    
    def add_info_message(self, message, duration=2.0):
        """Convenience method for general info"""
        self.add_notification(message, duration=duration, color=WHITE, position="top")
    
    def update(self, dt):
        """Update notification timers
        
        Args:
            dt (float): Time delta in seconds
        """
        # Update timers and remove expired notifications
        updated_notifications = []
        for notif in self.notifications:
            notif['timer'] -= dt
            if notif['timer'] > 0:
                updated_notifications.append(notif)

        self.notifications = updated_notifications

    def render(self, screen):
        """Render all active notifications

        Args:
            screen (pygame.Surface): Screen to render on
        """

        # Group notifications by position
        position_groups = {}
        for notif in self.notifications:
            pos = notif['position']
            if pos not in position_groups:
                position_groups[pos] = []
            position_groups[pos].append(notif)

        # Render each group
        for position, group in position_groups.items():
            self._render_group(screen, group, position)
    
    def _render_group(self, screen, notifications, position):
        """Render a group of notifications at specific position
        
        Args:
            screen (pygame.Surface): Screen to render on
            notifications (list): List of notifications to render
            position (str): Position identifier
        """
        screen_width = screen.get_width()
        screen_height = screen.get_height()
        
        # Calculate starting position
        if position == "center":
            start_x = screen_width // 2
            start_y = screen_height // 2
            align = "center"
        elif position == "center-bottom":
            start_x = screen_width // 2
            start_y = screen_height - 100
            align = "center"
        elif position == "top":
            start_x = screen_width // 2
            start_y = 30
            align = "center"
        elif position == "top-left":
            start_x = 20
            start_y = 30
            align = "left"
        elif position == "bottom":
            start_x = screen_width // 2
            start_y = screen_height - 50
            align = "center"
        else:
            # Default to center
            start_x = screen_width // 2
            start_y = screen_height // 2
            align = "center"
        
        # Render each notification in the group
        offset_y = 0
        for notif in notifications:
            surface = notif['surface']
            
            # Calculate final position
            if align == "center":
                x = start_x - surface.get_width() // 2
            else:  # left align
                x = start_x
            
            y = start_y + offset_y
            
            # Add fade effect based on remaining time
            alpha = min(255, int(255 * min(notif['timer'], 1.0)))
            surface.set_alpha(alpha)
            
            # Render with shadow for better readability
            shadow_surface = self.font.render(notif['message'], True, BLACK)
            shadow_surface.set_alpha(alpha // 2)
            screen.blit(shadow_surface, (x + 2, y + 2))
            screen.blit(surface, (x, y))
            
            offset_y += surface.get_height() + 5


class GameUI:
    """Main UI system for the game"""
    
    def __init__(self):
        """Initialize the UI system"""
        self.notification_system = NotificationSystem()
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        
        # UI state
        self.show_debug = False
    
    def show_pickup_message(self, message):
        """Show a pickup notification
        
        Args:
            message (str): Pickup message to display
        """
        self.notification_system.add_pickup_message(message)
    
    def show_damage_message(self, damage):
        """Show damage taken notification
        
        Args:
            damage (int): Amount of damage taken
        """
        self.notification_system.add_damage_message(f"-{damage} HP")
    
    def show_info_message(self, message, duration=2.0):
        """Show general information message
        
        Args:
            message (str): Information to display
            duration (float): How long to show
        """
        self.notification_system.add_info_message(message, duration)
    
    def update(self, dt):
        """Update UI systems
        
        Args:
            dt (float): Time delta in seconds
        """
        self.notification_system.update(dt)

    def render_hud(self, screen, player, score, fps=0):
        """Render the heads-up display
        
        Args:
            screen (pygame.Surface): Screen to render on
            player: Player object with health info
            score (int): Current score
            fps (float): Current FPS
        """
        # Health bar
        self._render_health_bar(screen, player.health, player.max_health)
        
        # Score
        score_text = self.font.render(f"Score: {score}", True, WHITE)
        screen.blit(score_text, (10, 50))
        
        # Current weapon info
        if hasattr(player, 'current_weapon') and player.current_weapon:
            weapon = player.current_weapon
            weapon_text = f"{weapon.name}: {weapon.ammo}/{weapon.magazine_size}"
            if weapon.is_reloading:
                weapon_text += " (Reloading...)"
            
            weapon_surface = self.small_font.render(weapon_text, True, WHITE)
            screen.blit(weapon_surface, (10, 80))
        
        # FPS (if enabled)
        if self.show_debug and fps > 0:
            fps_text = self.small_font.render(f"FPS: {fps:.1f}", True, WHITE)
            screen.blit(fps_text, (WINDOW_WIDTH - 100, 10))
    
    def _render_health_bar(self, screen, current_health, max_health):
        """Render health bar
        
        Args:
            screen (pygame.Surface): Screen to render on
            current_health (float): Current health value
            max_health (float): Maximum health value
        """
        bar_width = 200
        bar_height = 20
        x, y = 10, 10
        
        # Background (black)
        pygame.draw.rect(screen, BLACK, (x, y, bar_width, bar_height))
        
        # Health fill (red to green gradient based on health percentage)
        health_percentage = current_health / max_health
        fill_width = int(bar_width * health_percentage)
        
        if health_percentage > 0.6:
            color = GREEN
        elif health_percentage > 0.3:
            color = (255, 255, 0)  # Yellow
        else:
            color = RED
        
        if fill_width > 0:
            pygame.draw.rect(screen, color, (x, y, fill_width, bar_height))
        
        # Border (white)
        pygame.draw.rect(screen, WHITE, (x, y, bar_width, bar_height), 2)
        
        # Health text
        health_text = f"{int(current_health)}/{int(max_health)}"
        text_surface = self.small_font.render(health_text, True, WHITE)
        text_x = x + bar_width // 2 - text_surface.get_width() // 2
        text_y = y + bar_height // 2 - text_surface.get_height() // 2
        screen.blit(text_surface, (text_x, text_y))
    
    def render_notifications(self, screen):
        """Render all notifications
        
        Args:
            screen (pygame.Surface): Screen to render on
        """
        self.notification_system.render(screen)
    
    def toggle_debug(self):
        """Toggle debug information display"""
        self.show_debug = not self.show_debug