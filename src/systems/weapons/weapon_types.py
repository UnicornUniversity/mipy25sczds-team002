import pygame
import random
import math
from utils.constants import (
    # Pistol constants
    PISTOL_DAMAGE, PISTOL_SPREAD, PISTOL_MAGAZINE_SIZE, PISTOL_RELOAD_TIME, PISTOL_COOLDOWN,
    # Shotgun constants
    SHOTGUN_DAMAGE, SHOTGUN_PELLETS, SHOTGUN_SPREAD, SHOTGUN_MAGAZINE_SIZE, SHOTGUN_RELOAD_TIME, SHOTGUN_COOLDOWN,
    # Assault Rifle constants
    ASSAULT_RIFLE_DAMAGE, ASSAULT_RIFLE_SPREAD, ASSAULT_RIFLE_MAGAZINE_SIZE, ASSAULT_RIFLE_RELOAD_TIME,
    ASSAULT_RIFLE_COOLDOWN,
    # Sniper Rifle constants
    SNIPER_RIFLE_DAMAGE, SNIPER_RIFLE_SPREAD, SNIPER_RIFLE_MAGAZINE_SIZE, SNIPER_RIFLE_RELOAD_TIME,
    SNIPER_RIFLE_COOLDOWN,
    # Bazooka constants
    BAZOOKA_DAMAGE, BAZOOKA_SPREAD, BAZOOKA_MAGAZINE_SIZE, BAZOOKA_RELOAD_TIME, BAZOOKA_COOLDOWN,
)


class Weapon:
    """Base class for all weapons - čistá weapon logika bez rendering"""

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

    def _calculate_weapon_position(self, player_x, player_y, aim_angle):
        """Calculate weapon muzzle position based on player position and aim angle

        Args:
            player_x (float): Player center x position
            player_y (float): Player center y position
            aim_angle (float): Aim angle in radians

        Returns:
            tuple: (weapon_x, weapon_y) - Weapon muzzle position
        """
        # Jednoduchý offset - zbraň je prostě kousek dopředu ve směru míření
        # a trochu napravo (když se díváme ve směru míření)

        # Vzdálenost dopředu (ve směru míření)
        forward_distance = 30

        # Vzdálenost napravo (kolmo na směr míření)
        right_distance = 12

        # Výpočet pozice dopředu
        forward_x = player_x + math.cos(aim_angle) * forward_distance
        forward_y = player_y + math.sin(aim_angle) * forward_distance

        # Výpočet pravého offsetu (90° vpravo od směru míření)
        right_angle = aim_angle + math.pi / 2
        weapon_x = forward_x + math.cos(right_angle) * right_distance
        weapon_y = forward_y + math.sin(right_angle) * right_distance

        return weapon_x, weapon_y

    def shoot(self, x, y, angle):
        """Attempt to shoot a bullet

        Args:
            x (float): Player center x position
            y (float): Player center y position
            angle (float): Angle in radians

        Returns:
            Projectile or list or None: A new projectile(s) if shot was successful, None otherwise
        """
        # Check if weapon can shoot
        if self.cooldown_timer > 0 or self.is_reloading or self.ammo <= 0:
            return None

        # Reset cooldown timer
        self.cooldown_timer = self.cooldown

        # Decrease ammo
        self.ammo -= 1

        # Calculate actual weapon position
        weapon_x, weapon_y = self._calculate_weapon_position(x, y, angle)

        # Apply spread to angle
        spread_angle = angle + random.uniform(-self.spread, self.spread)

        # Import here to avoid circular imports
        from .projectiles import Bullet
        return Bullet(weapon_x, weapon_y, spread_angle, self.damage)

    def get_muzzle_position(self, player_x, player_y, aim_angle):
        """Get weapon muzzle position for effects like muzzle flash

        Args:
            player_x (float): Player center x position
            player_y (float): Player center y position
            aim_angle (float): Aim angle in radians

        Returns:
            tuple: (muzzle_x, muzzle_y) - Muzzle position
        """
        return self._calculate_weapon_position(player_x, player_y, aim_angle)

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

    def get_weapon_type(self):
        """Get weapon type string for identification

        Returns:
            str: Weapon type identifier
        """
        return self.name.lower().replace(' ', '_')


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
        """Shoot a pistol bullet"""
        if not self.can_shoot():
            return None

        self.cooldown_timer = self.cooldown
        self.ammo -= 1

        # Calculate weapon position
        weapon_x, weapon_y = self._calculate_weapon_position(x, y, angle)
        spread_angle = angle + random.uniform(-self.spread, self.spread)

        from .projectiles import PistolBullet
        return PistolBullet(weapon_x, weapon_y, spread_angle, self.damage)


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

        Returns:
            list: List of pellets if shot was successful, None otherwise
        """
        if not self.can_shoot():
            return None

        self.cooldown_timer = self.cooldown
        self.ammo -= 1

        # Calculate weapon position
        weapon_x, weapon_y = self._calculate_weapon_position(x, y, angle)

        # Create multiple pellets with spread
        pellets = []
        from .projectiles import ShotgunPellet

        for _ in range(SHOTGUN_PELLETS):
            spread_angle = angle + random.uniform(-self.spread, self.spread)
            pellet = ShotgunPellet(weapon_x, weapon_y, spread_angle, self.damage)
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
        """Shoot an assault rifle bullet"""
        if not self.can_shoot():
            return None

        self.cooldown_timer = self.cooldown
        self.ammo -= 1

        # Calculate weapon position
        weapon_x, weapon_y = self._calculate_weapon_position(x, y, angle)
        spread_angle = angle + random.uniform(-self.spread, self.spread)

        from .projectiles import AssaultRifleBullet
        return AssaultRifleBullet(weapon_x, weapon_y, spread_angle, self.damage)


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
        """Shoot a sniper rifle bullet"""
        if not self.can_shoot():
            return None

        self.cooldown_timer = self.cooldown
        self.ammo -= 1

        # Calculate weapon position
        weapon_x, weapon_y = self._calculate_weapon_position(x, y, angle)
        spread_angle = angle + random.uniform(-self.spread, self.spread)

        from .projectiles import SniperRifleBullet
        return SniperRifleBullet(weapon_x, weapon_y, spread_angle, self.damage)


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
        """Shoot a bazooka rocket"""
        if not self.can_shoot():
            return None

        self.cooldown_timer = self.cooldown
        self.ammo -= 1

        # Calculate weapon position
        weapon_x, weapon_y = self._calculate_weapon_position(x, y, angle)
        spread_angle = angle + random.uniform(-self.spread, self.spread)

        from .projectiles import BazookaRocket
        return BazookaRocket(weapon_x, weapon_y, spread_angle, self.damage)