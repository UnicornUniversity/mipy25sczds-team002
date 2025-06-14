import pygame
import random
import math

class Effect:
    """Base class for visual effects"""
    
    def __init__(self, x, y, duration=0.5):
        """Initialize the effect
        
        Args:
            x (float): X position
            y (float): Y position
            duration (float): Duration in seconds
        """
        self.x = x
        self.y = y
        self.duration = duration
        self.timer = duration
        self.finished = False
    
    def update(self, dt):
        """Update the effect
        
        Args:
            dt (float): Time delta in seconds
        """
        self.timer -= dt
        if self.timer <= 0:
            self.finished = True
    
    def render(self, screen, camera_offset=(0, 0)):
        """Render the effect
        
        Args:
            screen (pygame.Surface): Screen to render on
            camera_offset (tuple): Camera offset (x, y)
        """
        pass

class MuzzleFlash(Effect):
    """Muzzle flash effect when a weapon is fired"""
    
    def __init__(self, x, y, angle, color=(255, 255, 0), size=10, duration=0.1):
        """Initialize the muzzle flash
        
        Args:
            x (float): X position
            y (float): Y position
            angle (float): Angle in radians
            color (tuple): RGB color tuple
            size (int): Size of the flash
            duration (float): Duration in seconds
        """
        super().__init__(x, y, duration)
        self.angle = angle
        self.color = color
        self.size = size
        self.alpha = 255  # Start fully opaque
    
    def update(self, dt):
        """Update the muzzle flash
        
        Args:
            dt (float): Time delta in seconds
        """
        super().update(dt)
        
        # Fade out over time
        self.alpha = int(255 * (self.timer / self.duration))
    
    def render(self, screen, camera_offset=(0, 0)):
        """Render the muzzle flash
        
        Args:
            screen (pygame.Surface): Screen to render on
            camera_offset (tuple): Camera offset (x, y)
        """
        # Calculate screen position
        screen_x = self.x - camera_offset[0]
        screen_y = self.y - camera_offset[1]
        
        # Create a surface with per-pixel alpha
        flash_surface = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
        
        # Draw the flash as a triangle pointing in the direction of the angle
        points = [
            (self.size, self.size),  # Center
            (self.size + math.cos(self.angle) * self.size * 2, self.size + math.sin(self.angle) * self.size * 2),  # Tip
            (self.size + math.cos(self.angle + 0.5) * self.size, self.size + math.sin(self.angle + 0.5) * self.size),  # Side point
            (self.size + math.cos(self.angle - 0.5) * self.size, self.size + math.sin(self.angle - 0.5) * self.size)   # Side point
        ]
        
        # Draw the flash with the current alpha
        pygame.draw.polygon(flash_surface, (*self.color, self.alpha), points)
        
        # Blit the surface to the screen
        screen.blit(flash_surface, (screen_x - self.size, screen_y - self.size))

class BulletImpact(Effect):
    """Bullet impact effect when a bullet hits something"""
    
    def __init__(self, x, y, color=(255, 255, 255), size=5, duration=0.3):
        """Initialize the bullet impact
        
        Args:
            x (float): X position
            y (float): Y position
            color (tuple): RGB color tuple
            size (int): Size of the impact
            duration (float): Duration in seconds
        """
        super().__init__(x, y, duration)
        self.color = color
        self.size = size
        self.particles = []
        
        # Create particles
        for _ in range(10):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(50, 100)
            self.particles.append({
                'x': x,
                'y': y,
                'vx': math.cos(angle) * speed,
                'vy': math.sin(angle) * speed,
                'size': random.uniform(1, 3)
            })
    
    def update(self, dt):
        """Update the bullet impact
        
        Args:
            dt (float): Time delta in seconds
        """
        super().update(dt)
        
        # Update particles
        for particle in self.particles:
            particle['x'] += particle['vx'] * dt
            particle['y'] += particle['vy'] * dt
            particle['size'] -= dt * 5  # Shrink over time
    
    def render(self, screen, camera_offset=(0, 0)):
        """Render the bullet impact
        
        Args:
            screen (pygame.Surface): Screen to render on
            camera_offset (tuple): Camera offset (x, y)
        """
        # Calculate alpha based on remaining time
        alpha = int(255 * (self.timer / self.duration))
        
        # Render particles
        for particle in self.particles:
            if particle['size'] <= 0:
                continue
                
            # Calculate screen position
            screen_x = particle['x'] - camera_offset[0]
            screen_y = particle['y'] - camera_offset[1]
            
            # Draw particle
            pygame.draw.circle(screen, (*self.color, alpha), (int(screen_x), int(screen_y)), int(particle['size']))

class BloodSplatter(Effect):
    """Blood splatter effect when a zombie takes damage"""
    
    def __init__(self, x, y, color=(255, 0, 0), size=8, duration=0.5):
        """Initialize the blood splatter
        
        Args:
            x (float): X position
            y (float): Y position
            color (tuple): RGB color tuple
            size (int): Size of the splatter
            duration (float): Duration in seconds
        """
        super().__init__(x, y, duration)
        self.color = color
        self.size = size
        self.drops = []
        
        # Create blood drops
        for _ in range(15):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(30, 80)
            self.drops.append({
                'x': x,
                'y': y,
                'vx': math.cos(angle) * speed,
                'vy': math.sin(angle) * speed,
                'size': random.uniform(2, 4)
            })
    
    def update(self, dt):
        """Update the blood splatter
        
        Args:
            dt (float): Time delta in seconds
        """
        super().update(dt)
        
        # Update blood drops
        for drop in self.drops:
            drop['x'] += drop['vx'] * dt
            drop['y'] += drop['vy'] * dt
            
            # Slow down over time (simulate gravity and friction)
            drop['vx'] *= 0.95
            drop['vy'] *= 0.95
    
    def render(self, screen, camera_offset=(0, 0)):
        """Render the blood splatter
        
        Args:
            screen (pygame.Surface): Screen to render on
            camera_offset (tuple): Camera offset (x, y)
        """
        # Calculate alpha based on remaining time
        alpha = int(255 * (self.timer / self.duration))
        
        # Render blood drops
        for drop in self.drops:
            # Calculate screen position
            screen_x = drop['x'] - camera_offset[0]
            screen_y = drop['y'] - camera_offset[1]
            
            # Draw blood drop
            pygame.draw.circle(screen, (*self.color, alpha), (int(screen_x), int(screen_y)), int(drop['size']))