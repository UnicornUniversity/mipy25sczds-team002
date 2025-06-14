import pygame
import random
import math
from entities.entity import Entity
from utils.constants import (
    BULLET_SIZE, BULLET_SPEED, BULLET_COLOR,
    PISTOL_DAMAGE, PISTOL_SPREAD, PISTOL_MAGAZINE_SIZE, PISTOL_RELOAD_TIME,
    WEAPON_COOLDOWN
)

class Weapon:
    """Base class for all weapons"""
    
    def __init__(self, name, damage, spread, magazine_size, reload_time, cooldown):
        """Initialize the weapon
        
        Args:
            name (str): Weapon name
            damage (int): Damage per bullet
            spread (float): Accuracy spread in radians
            magazine_size (int): Number of bullets in magazine
            reload_time (float): Time to reload in seconds
            cooldown (float): Time between shots in seconds
        """
        self.name = name
        self.damage = damage
        self.spread = spread
        self.magazine_size = magazine_size
        self.reload_time = reload_time
        self.cooldown = cooldown
        
        # Current state
        self.ammo = magazine_size
        self.is_reloading = False
        self.reload_timer = 0
        self.cooldown_timer = 0
        
    def update(self, dt):
        """Update weapon state
        
        Args:
            dt (float): Time delta in seconds
        """
        # Update cooldown timer
        if self.cooldown_timer > 0:
            self.cooldown_timer -= dt
            
        # Update reload timer
        if self.is_reloading:
            self.reload_timer -= dt
            if self.reload_timer <= 0:
                self.ammo = self.magazine_size
                self.is_reloading = False
    
    def shoot(self, x, y, angle):
        """Attempt to shoot a bullet
        
        Args:
            x (float): Starting x position
            y (float): Starting y position
            angle (float): Angle in radians
            
        Returns:
            Bullet or None: A new bullet if shot was successful, None otherwise
        """
        # Check if weapon can shoot
        if self.cooldown_timer > 0 or self.is_reloading or self.ammo <= 0:
            return None
            
        # Reset cooldown timer
        self.cooldown_timer = self.cooldown
        
        # Decrease ammo
        self.ammo -= 1
        
        # Apply spread to angle
        spread_angle = angle + random.uniform(-self.spread, self.spread)
        
        # Create a new bullet
        return Bullet(x, y, spread_angle, self.damage)
    
    def reload(self):
        """Start reloading the weapon"""
        if not self.is_reloading and self.ammo < self.magazine_size:
            self.is_reloading = True
            self.reload_timer = self.reload_time
            
    def can_shoot(self):
        """Check if weapon can shoot
        
        Returns:
            bool: True if weapon can shoot, False otherwise
        """
        return not self.is_reloading and self.ammo > 0 and self.cooldown_timer <= 0

class Pistol(Weapon):
    """Pistol weapon"""
    
    def __init__(self):
        """Initialize the pistol"""
        super().__init__(
            name="Pistol",
            damage=PISTOL_DAMAGE,
            spread=PISTOL_SPREAD,
            magazine_size=PISTOL_MAGAZINE_SIZE,
            reload_time=PISTOL_RELOAD_TIME,
            cooldown=WEAPON_COOLDOWN
        )

class Bullet(Entity):
    """Bullet entity"""
    
    def __init__(self, x, y, angle, damage):
        """Initialize the bullet
        
        Args:
            x (float): Initial x position
            y (float): Initial y position
            angle (float): Movement angle in radians
            damage (int): Damage amount
        """
        super().__init__(x, y, BULLET_SIZE, BULLET_SIZE, BULLET_COLOR)
        self.angle = angle
        self.damage = damage
        self.speed = BULLET_SPEED
        self.distance_traveled = 0
        self.max_distance = 1000  # Maximum travel distance before bullet disappears
        
    def update(self, dt, map_generator=None):
        """Update bullet position
        
        Args:
            dt (float): Time delta in seconds
            map_generator (MapGenerator, optional): Reference to the map generator
        """
        # Calculate movement vector
        dx = math.cos(self.angle) * self.speed * dt
        dy = math.sin(self.angle) * self.speed * dt
        
        # Update position
        self.x += dx
        self.y += dy
        
        # Update distance traveled
        self.distance_traveled += math.sqrt(dx * dx + dy * dy)
        
        # Check for collision with map if map_generator is provided
        if map_generator and not map_generator.is_walkable(self.x, self.y):
            self.distance_traveled = self.max_distance  # Mark for removal
            
        # Call parent update to update rect
        super().update(dt)
        
    def is_expired(self):
        """Check if bullet has expired
        
        Returns:
            bool: True if bullet has traveled its maximum distance, False otherwise
        """
        return self.distance_traveled >= self.max_distance
        
    def render(self, screen, camera_offset=(0, 0)):
        """Render the bullet as a small circle
        
        Args:
            screen (pygame.Surface): Screen to render on
            camera_offset (tuple): Camera offset (x, y)
        """
        # Calculate center position
        center_x = self.rect.x + self.width // 2 - camera_offset[0]
        center_y = self.rect.y + self.height // 2 - camera_offset[1]
        
        # Draw bullet as a small circle
        pygame.draw.circle(screen, self.color, (center_x, center_y), self.width // 2)
