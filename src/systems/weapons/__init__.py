"""
Usage:
    from systems.weapons import WeaponFactory, WeaponInventory

    # Create weapon inventory for player
    inventory = WeaponInventory(max_weapons=5)

    # Create and add weapon
    pistol = WeaponFactory.create_weapon("pistol")
    inventory.add_weapon(pistol, auto_switch=True)
"""

from .weapon_factory import WeaponFactory, WeaponType
from .weapon_inventory import WeaponInventory
from .weapon_types import Weapon, Pistol, Shotgun, AssaultRifle, SniperRifle, Bazooka
from .projectiles import (
    Bullet, PistolBullet, ShotgunPellet, AssaultRifleBullet,
    SniperRifleBullet, BazookaRocket
)

__all__ = [
    # Factory and management
    'WeaponFactory', 'WeaponType', 'WeaponInventory',

    # Weapon types
    'Weapon', 'Pistol', 'Shotgun', 'AssaultRifle', 'SniperRifle', 'Bazooka',

    # Projectiles
    'Bullet', 'PistolBullet', 'ShotgunPellet', 'AssaultRifleBullet',
    'SniperRifleBullet', 'BazookaRocket'
]