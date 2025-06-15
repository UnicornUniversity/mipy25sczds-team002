import pygame
import math
from entities.entity import Entity
from systems import collisions
from utils.constants import (
    BULLET_SIZE, BULLET_SPEED, BULLET_COLOR,
    # Weapon-specific bullet colors and speeds
    PISTOL_BULLET_COLOR, SHOTGUN_BULLET_COLOR, ASSAULT_RIFLE_BULLET_COLOR,
    SNIPER_RIFLE_BULLET_COLOR, SNIPER_RIFLE_BULLET_SPEED,
    BAZOOKA_BULLET_COLOR, BAZOOKA_BULLET_SPEED, BAZOOKA_EXPLOSION_RADIUS,
    MAP_WIDTH, MAP_HEIGHT, TILE_SIZE
)


class Bullet(Entity):
    """Base bullet entity - základní projektil"""

    def __init__(self, x, y, angle, damage, color=BULLET_COLOR, speed=BULLET_SPEED, size=BULLET_SIZE):
        """Initialize the bullet

        Args:
            x (float): Initial x position
            y (float): Initial y position
            angle (float): Movement angle in radians
            damage (int): Damage amount
            color (tuple): RGB color tuple
            speed (float): Bullet speed in pixels per second
            size (int): Bullet size in pixels
        """
        super().__init__(x, y, size, size, color)
        self.angle = angle
        self.damage = damage
        self.speed = speed
        self.distance_traveled = 0
        self.max_distance = 1500  # Increased default range
        self.is_explosive = False  # Whether the bullet explodes on impact
        self.explosion_radius = 0  # Explosion radius in pixels
        self.lifetime = 0  # Track lifetime for effects
        self.min_travel_time = 0.05  # Minimum time before collision checks (prevents instant collision)

    def update(self, dt, map_generator=None):
        """Update bullet position

        Args:
            dt (float): Time delta in seconds
            map_generator (MapGenerator, optional): Reference to the map generator
        """
        # Update lifetime
        self.lifetime += dt

        # Calculate movement vector
        dx = math.cos(self.angle) * self.speed * dt
        dy = math.sin(self.angle) * self.speed * dt

        # Update position
        old_x, old_y = self.x, self.y
        self.x += dx
        self.y += dy

        # Update distance traveled
        self.distance_traveled += math.sqrt(dx * dx + dy * dy)

        # Check map boundaries first (bullets disappear when leaving map)
        map_width_px = MAP_WIDTH * TILE_SIZE
        map_height_px = MAP_HEIGHT * TILE_SIZE

        if (self.x < 0 or self.x > map_width_px or
                self.y < 0 or self.y > map_height_px):
            self.distance_traveled = self.max_distance  # Mark for removal
            return

        # Only check wall collision after minimum travel time to prevent instant hits
        if self.lifetime > self.min_travel_time:
            # Check for collision with walls using the collision system
            if map_generator and not collisions.is_position_walkable(self.x + self.width / 2, self.y + self.height / 2):
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
        """Render the bullet as a small circle with trail effect

        Args:
            screen (pygame.Surface): Screen to render on
            camera_offset (tuple): Camera offset (x, y)
        """
        # Calculate center position
        center_x = int(self.rect.x + self.width // 2 - camera_offset[0])
        center_y = int(self.rect.y + self.height // 2 - camera_offset[1])

        # Draw bullet as a small circle
        pygame.draw.circle(screen, self.color, (center_x, center_y), max(2, self.width // 2))

        # Add slight trail effect for fast bullets
        if self.speed > 600:
            trail_length = min(15, int(self.speed / 40))
            trail_end_x = int(center_x - math.cos(self.angle) * trail_length)
            trail_end_y = int(center_y - math.sin(self.angle) * trail_length)

            # Draw fading trail
            for i in range(3):
                alpha = 100 - (i * 30)
                trail_pos_x = int(center_x - math.cos(self.angle) * (trail_length * (i + 1) / 3))
                trail_pos_y = int(center_y - math.sin(self.angle) * (trail_length * (i + 1) / 3))

                # Create surface with alpha for trail
                trail_surface = pygame.Surface((4, 4), pygame.SRCALPHA)
                trail_color = (*self.color, alpha)
                pygame.draw.circle(trail_surface, trail_color, (2, 2), 2)
                screen.blit(trail_surface, (trail_pos_x - 2, trail_pos_y - 2))

    def explode(self):
        """Handle explosion for explosive bullets

        Returns:
            dict or None: Explosion data for game state to handle, or None for non-explosive bullets
        """
        if self.is_explosive:
            # Mark the bullet as expired
            self.distance_traveled = self.max_distance

            return {
                'position': (self.x, self.y),
                'radius': self.explosion_radius,
                'damage': self.damage
            }
        return None


class PistolBullet(Bullet):
    """Pistol bullet - Standard bullet with medium speed and damage"""

    def __init__(self, x, y, angle, damage):
        """Initialize the pistol bullet"""
        super().__init__(
            x=x,
            y=y,
            angle=angle,
            damage=damage,
            color=PISTOL_BULLET_COLOR,
            speed=BULLET_SPEED,  # 500 px/s
            size=BULLET_SIZE
        )
        self.max_distance = 1200


class ShotgunPellet(Bullet):
    """Shotgun pellet - Small, fast bullet with low damage but shorter range"""

    def __init__(self, x, y, angle, damage):
        """Initialize the shotgun pellet"""
        super().__init__(
            x=x,
            y=y,
            angle=angle,
            damage=damage,
            color=SHOTGUN_BULLET_COLOR,
            speed=BULLET_SPEED * 1.4,  # 700 px/s - faster than pistol
            size=BULLET_SIZE - 2  # Smaller
        )
        self.max_distance = 600  # Much shorter range than regular bullets


class AssaultRifleBullet(Bullet):
    """Assault rifle bullet - Fast bullet with medium damage"""

    def __init__(self, x, y, angle, damage):
        """Initialize the assault rifle bullet"""
        super().__init__(
            x=x,
            y=y,
            angle=angle,
            damage=damage,
            color=ASSAULT_RIFLE_BULLET_COLOR,
            speed=BULLET_SPEED * 1.3,  # 650 px/s
            size=BULLET_SIZE
        )
        self.max_distance = 1400


class SniperRifleBullet(Bullet):
    """Sniper rifle bullet - Very fast bullet with high damage and long range"""

    def __init__(self, x, y, angle, damage):
        """Initialize the sniper rifle bullet"""
        super().__init__(
            x=x,
            y=y,
            angle=angle,
            damage=damage,
            color=SNIPER_RIFLE_BULLET_COLOR,
            speed=SNIPER_RIFLE_BULLET_SPEED,  # 800 px/s - much faster
            size=BULLET_SIZE + 2  # Slightly larger
        )
        self.max_distance = 2500  # Very long range
        self.min_travel_time = 0.02  # Even less delay for sniper


class BazookaRocket(Bullet):
    """Bazooka rocket - Slow bullet with explosive damage"""

    def __init__(self, x, y, angle, damage):
        """Initialize the bazooka rocket"""
        super().__init__(
            x=x,
            y=y,
            angle=angle,
            damage=damage,
            color=BAZOOKA_BULLET_COLOR,
            speed=BAZOOKA_BULLET_SPEED,  # 300 px/s - much slower
            size=BULLET_SIZE * 3  # Much larger
        )
        self.is_explosive = True
        self.explosion_radius = BAZOOKA_EXPLOSION_RADIUS
        self.max_distance = 1800
        self.min_travel_time = 0.1  # Longer delay for rockets

    def render(self, screen, camera_offset=(0, 0)):
        """Render the rocket as a larger circle with a visible trail

        Args:
            screen (pygame.Surface): Screen to render on
            camera_offset (tuple): Camera offset (x, y)
        """
        # Calculate center position
        center_x = int(self.rect.x + self.width // 2 - camera_offset[0])
        center_y = int(self.rect.y + self.height // 2 - camera_offset[1])

        # Draw rocket body as a larger circle
        pygame.draw.circle(screen, self.color, (center_x, center_y), self.width // 2)

        # Draw rocket tip (slightly darker)
        tip_color = tuple(max(0, c - 50) for c in self.color)
        tip_x = int(center_x + math.cos(self.angle) * (self.width // 3))
        tip_y = int(center_y + math.sin(self.angle) * (self.width // 3))
        pygame.draw.circle(screen, tip_color, (tip_x, tip_y), self.width // 4)

        # Draw a prominent flame trail behind the rocket
        trail_length = 40
        for i in range(8):
            trail_distance = (i + 1) * (trail_length / 8)
            trail_x = int(center_x - math.cos(self.angle) * trail_distance)
            trail_y = int(center_y - math.sin(self.angle) * trail_distance)

            # Flame colors from orange to red
            flame_intensity = 255 - (i * 25)
            flame_color = (flame_intensity, max(100, flame_intensity - 100), 0)
            trail_radius = max(1, (8 - i) // 2)

            pygame.draw.circle(screen, flame_color, (trail_x, trail_y), trail_radius)

    def explode(self):
        """Handle explosion for bazooka rocket

        Returns:
            dict: Explosion data for game state to handle
        """
        # Mark the bullet as expired
        self.distance_traveled = self.max_distance

        return {
            'position': (self.x + self.width // 2, self.y + self.height // 2),  # Center of rocket
            'radius': self.explosion_radius,
            'damage': self.damage
        }