import pygame
import random
import math
from entities.entity import Entity
from systems import collisions
from utils.constants import (
    BULLET_SIZE, BULLET_SPEED, BULLET_COLOR,
    # Pistol constants
    PISTOL_DAMAGE, PISTOL_SPREAD, PISTOL_MAGAZINE_SIZE, PISTOL_RELOAD_TIME, PISTOL_COOLDOWN, PISTOL_BULLET_COLOR,
    # Shotgun constants
    SHOTGUN_DAMAGE, SHOTGUN_PELLETS, SHOTGUN_SPREAD, SHOTGUN_MAGAZINE_SIZE, SHOTGUN_RELOAD_TIME, SHOTGUN_COOLDOWN, SHOTGUN_BULLET_COLOR,
    # Assault Rifle constants
    ASSAULT_RIFLE_DAMAGE, ASSAULT_RIFLE_SPREAD, ASSAULT_RIFLE_MAGAZINE_SIZE, ASSAULT_RIFLE_RELOAD_TIME, ASSAULT_RIFLE_COOLDOWN, ASSAULT_RIFLE_BULLET_COLOR,
    # Sniper Rifle constants
    SNIPER_RIFLE_DAMAGE, SNIPER_RIFLE_SPREAD, SNIPER_RIFLE_MAGAZINE_SIZE, SNIPER_RIFLE_RELOAD_TIME, SNIPER_RIFLE_COOLDOWN, SNIPER_RIFLE_BULLET_COLOR, SNIPER_RIFLE_BULLET_SPEED,
    # Bazooka constants
    BAZOOKA_DAMAGE, BAZOOKA_SPREAD, BAZOOKA_MAGAZINE_SIZE, BAZOOKA_RELOAD_TIME, BAZOOKA_COOLDOWN, BAZOOKA_BULLET_COLOR, BAZOOKA_EXPLOSION_RADIUS, BAZOOKA_BULLET_SPEED,
    # General weapon settings
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
    """Pistol weapon - Balanced damage/fire rate"""

    def __init__(self):
        """Initialize the pistol"""
        super().__init__(
            name="Pistol",
            damage=PISTOL_DAMAGE,
            spread=PISTOL_SPREAD,
            magazine_size=PISTOL_MAGAZINE_SIZE,
            reload_time=PISTOL_RELOAD_TIME,
            cooldown=PISTOL_COOLDOWN
        )

    def shoot(self, x, y, angle):
        """Shoot a pistol bullet

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
        return PistolBullet(x, y, spread_angle, self.damage)

class Shotgun(Weapon):
    """Shotgun weapon - High damage at close range, slow reload"""

    def __init__(self):
        """Initialize the shotgun"""
        super().__init__(
            name="Shotgun",
            damage=SHOTGUN_DAMAGE,
            spread=SHOTGUN_SPREAD,
            magazine_size=SHOTGUN_MAGAZINE_SIZE,
            reload_time=SHOTGUN_RELOAD_TIME,
            cooldown=SHOTGUN_COOLDOWN
        )

    def shoot(self, x, y, angle):
        """Shoot multiple shotgun pellets

        Args:
            x (float): Starting x position
            y (float): Starting y position
            angle (float): Angle in radians

        Returns:
            list or None: A list of pellets if shot was successful, None otherwise
        """
        # Check if weapon can shoot
        if self.cooldown_timer > 0 or self.is_reloading or self.ammo <= 0:
            return None

        # Reset cooldown timer
        self.cooldown_timer = self.cooldown

        # Decrease ammo
        self.ammo -= 1

        # Create multiple pellets with spread
        pellets = []
        for _ in range(SHOTGUN_PELLETS):
            # Apply spread to angle
            spread_angle = angle + random.uniform(-self.spread, self.spread)

            # Create a new pellet
            pellet = ShotgunPellet(x, y, spread_angle, self.damage)
            pellets.append(pellet)

        return pellets

class AssaultRifle(Weapon):
    """Assault Rifle weapon - Rapid fire, medium damage"""

    def __init__(self):
        """Initialize the assault rifle"""
        super().__init__(
            name="Assault Rifle",
            damage=ASSAULT_RIFLE_DAMAGE,
            spread=ASSAULT_RIFLE_SPREAD,
            magazine_size=ASSAULT_RIFLE_MAGAZINE_SIZE,
            reload_time=ASSAULT_RIFLE_RELOAD_TIME,
            cooldown=ASSAULT_RIFLE_COOLDOWN
        )

    def shoot(self, x, y, angle):
        """Shoot an assault rifle bullet

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
        return AssaultRifleBullet(x, y, spread_angle, self.damage)

class SniperRifle(Weapon):
    """Sniper Rifle weapon - High damage, slow fire rate, high accuracy"""

    def __init__(self):
        """Initialize the sniper rifle"""
        super().__init__(
            name="Sniper Rifle",
            damage=SNIPER_RIFLE_DAMAGE,
            spread=SNIPER_RIFLE_SPREAD,
            magazine_size=SNIPER_RIFLE_MAGAZINE_SIZE,
            reload_time=SNIPER_RIFLE_RELOAD_TIME,
            cooldown=SNIPER_RIFLE_COOLDOWN
        )

    def shoot(self, x, y, angle):
        """Shoot a sniper rifle bullet

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

        # Apply spread to angle (very small spread for sniper)
        spread_angle = angle + random.uniform(-self.spread, self.spread)

        # Create a new bullet
        return SniperRifleBullet(x, y, spread_angle, self.damage)

class Bazooka(Weapon):
    """Bazooka weapon - Explosive damage, very slow fire rate"""

    def __init__(self):
        """Initialize the bazooka"""
        super().__init__(
            name="Bazooka",
            damage=BAZOOKA_DAMAGE,
            spread=BAZOOKA_SPREAD,
            magazine_size=BAZOOKA_MAGAZINE_SIZE,
            reload_time=BAZOOKA_RELOAD_TIME,
            cooldown=BAZOOKA_COOLDOWN
        )

    def shoot(self, x, y, angle):
        """Shoot a bazooka rocket

        Args:
            x (float): Starting x position
            y (float): Starting y position
            angle (float): Angle in radians

        Returns:
            Bullet or None: A new rocket if shot was successful, None otherwise
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

        # Create a new rocket
        return BazookaRocket(x, y, spread_angle, self.damage)

class Bullet(Entity):
    """Base bullet entity"""

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
        self.max_distance = 1000  # Maximum travel distance before bullet disappears
        self.is_explosive = False  # Whether the bullet explodes on impact
        self.explosion_radius = 0  # Explosion radius in pixels

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

        # Check for collision with map using the collision system
        if not collisions.is_position_walkable(self.x, self.y):
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

    def explode(self):
        """Handle explosion for explosive bullets

        Returns:
            list: List of entities hit by the explosion
        """
        # Base implementation does nothing
        return []

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
            speed=BULLET_SPEED,
            size=BULLET_SIZE
        )

class ShotgunPellet(Bullet):
    """Shotgun pellet - Small, fast bullet with low damage"""

    def __init__(self, x, y, angle, damage):
        """Initialize the shotgun pellet"""
        super().__init__(
            x=x,
            y=y,
            angle=angle,
            damage=damage,
            color=SHOTGUN_BULLET_COLOR,
            speed=BULLET_SPEED * 1.2,  # Slightly faster
            size=BULLET_SIZE - 2  # Smaller
        )
        self.max_distance = 500  # Shorter range

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
            speed=BULLET_SPEED * 1.1,  # Slightly faster
            size=BULLET_SIZE
        )

class SniperRifleBullet(Bullet):
    """Sniper rifle bullet - Very fast bullet with high damage"""

    def __init__(self, x, y, angle, damage):
        """Initialize the sniper rifle bullet"""
        super().__init__(
            x=x,
            y=y,
            angle=angle,
            damage=damage,
            color=SNIPER_RIFLE_BULLET_COLOR,
            speed=SNIPER_RIFLE_BULLET_SPEED,  # Much faster
            size=BULLET_SIZE + 2  # Slightly larger
        )
        self.max_distance = 2000  # Longer range

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
            speed=BAZOOKA_BULLET_SPEED,  # Slower
            size=BULLET_SIZE * 2  # Much larger
        )
        self.is_explosive = True
        self.explosion_radius = BAZOOKA_EXPLOSION_RADIUS

    def render(self, screen, camera_offset=(0, 0)):
        """Render the rocket as a larger circle with a trail

        Args:
            screen (pygame.Surface): Screen to render on
            camera_offset (tuple): Camera offset (x, y)
        """
        # Calculate center position
        center_x = self.rect.x + self.width // 2 - camera_offset[0]
        center_y = self.rect.y + self.height // 2 - camera_offset[1]

        # Draw rocket as a larger circle
        pygame.draw.circle(screen, self.color, (center_x, center_y), self.width // 2)

        # Draw a trail behind the rocket
        trail_length = 20
        trail_end_x = center_x - math.cos(self.angle) * trail_length
        trail_end_y = center_y - math.sin(self.angle) * trail_length

        # Draw trail as a line
        pygame.draw.line(screen, (255, 165, 0), (center_x, center_y), (trail_end_x, trail_end_y), 3)

    def explode(self):
        """Handle explosion for bazooka rocket

        Returns:
            list: List of entities hit by the explosion
        """
        # In a more complete implementation, this would check for entities within
        # the explosion radius and return them for damage calculation

        # For now, just mark the bullet as expired
        self.distance_traveled = self.max_distance
        return []
