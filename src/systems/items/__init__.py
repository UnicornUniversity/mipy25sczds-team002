"""
Items System Package - Comprehensive Item Management
==================================================

This package contains all item-related functionality including:
- Item base classes and types
- Item factory for creating items
- Item effects system
- Powerups and consumables

Main exports:
- Item: Base item class
- WeaponPickup: Weapon items that can be picked up
- HealthPack: Health restoration items
- AmmoPack: Ammunition items
- Powerup: Base powerup class
- SpeedBoost, DamageBoost, etc.: Specific powerups
- ItemFactory: Factory for creating items
- create_random_item, create_random_powerup: Convenience functions
"""

# Import all item types
from .item_types import (
    Item,
    WeaponPickup,
    HealthPack,
    AmmoPack,
    Powerup,
    SpeedBoost,
    DamageBoost,
    HealthRegeneration,
    Invincibility,
    RapidFire,
)

# Import factory and convenience functions
from .item_factory import (
    ItemFactory,
    create_random_item,
    create_random_powerup,
    create_health_pack,
    create_ammo_pack,
    create_weapon_pickup,
    create_powerup
)

# Import effects system
from .item_effects import (
    ItemEffect,
    HealthEffect,
    AmmoEffect,
    WeaponEffect,
    StatBoostEffect,
    TemporaryEffect,
    apply_item_effect,
    remove_effect
)

# Define what gets exported when someone does "from systems.items import *"
__all__ = [
    # Base classes
    'Item',
    'Powerup',

    # Pickup items
    'WeaponPickup',
    'HealthPack',
    'AmmoPack',

    # Powerups (only those that exist)
    'SpeedBoost',
    'DamageBoost',
    'HealthRegeneration',
    'Invincibility',
    'RapidFire',

    # Factory and creation functions
    'ItemFactory',
    'create_random_item',
    'create_random_powerup',
    'create_health_pack',
    'create_ammo_pack',
    'create_weapon_pickup',
    'create_powerup',

    # Effects system
    'ItemEffect',
    'HealthEffect',
    'AmmoEffect',
    'WeaponEffect',
    'StatBoostEffect',
    'TemporaryEffect',
    'apply_item_effect',
    'remove_effect'
]

# Convenience aliases for backward compatibility
Weapon = WeaponPickup  # Legacy alias

# Version info
__version__ = "1.0.0"
__author__ = "Deadlock Game Team"


# Package info for debugging
def get_package_info():
    """Get information about the items package

    Returns:
        dict: Package information
    """
    return {
        'version': __version__,
        'author': __author__,
        'total_item_types': len([cls for cls in __all__ if not callable(globals().get(cls))]),
        'factory_functions': len(
            [func for func in __all__ if callable(globals().get(func)) and func.startswith('create_')]),
        'powerup_types': len([cls for cls in __all__ if
                              'Boost' in cls or cls in ['Invincibility', 'RapidFire', 'HealthRegeneration']]),
        'effect_types': len([cls for cls in __all__ if 'Effect' in cls])
    }

# Optional: Print package info when imported (for debugging)
print(f"Items system loaded: {get_package_info()}")