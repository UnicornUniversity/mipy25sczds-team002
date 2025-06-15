import random
from .item_types import (
    ItemType, ItemRarity, Item, WeaponPickup, HealthPack, AmmoPack,
    Powerup, SpeedBoost, DamageBoost, HealthRegeneration, 
    Invincibility, RapidFire
)

class ItemFactory:
    """Factory pro vytváření item instancí s weighted spawning"""

    # Registry pro basic items
    _basic_item_registry = {
        ItemType.WEAPON.value: WeaponPickup,
        ItemType.HEALTH.value: HealthPack,
        ItemType.AMMO.value: AmmoPack,
    }

    # Registry pro powerupy
    _powerup_registry = {
        ItemType.SPEED_BOOST.value: SpeedBoost,
        ItemType.DAMAGE_BOOST.value: DamageBoost,
        ItemType.HEALTH_REGEN.value: HealthRegeneration,
        ItemType.INVINCIBILITY.value: Invincibility,
        ItemType.RAPID_FIRE.value: RapidFire
    }

    # Spawn weights pro basic items (higher = more common)
    _basic_item_weights = {
        ItemType.HEALTH.value: 40,  # Most common
        ItemType.AMMO.value: 30,
        ItemType.WEAPON.value: 20,  # Less common
    }

    # Spawn weights pro powerupy podle rarity
    _powerup_weights = {
        # Common powerups (70% chance)
        ItemType.SPEED_BOOST.value: 35,

        # Rare powerups (25% chance)
        ItemType.DAMAGE_BOOST.value: 10,
        ItemType.HEALTH_REGEN.value: 10,
        ItemType.RAPID_FIRE.value: 8,

        # Legendary powerups (5% chance)
        ItemType.INVINCIBILITY.value: 2,
    }

    # Weapon types pro weapon pickupy (pistol excluded as player always has it)
    _weapon_types = ["shotgun", "assault_rifle", "sniper_rifle", "bazooka"]
    _weapon_weights = [25, 20, 15, 5]  # Shotgun most common

    @classmethod
    def create_item(cls, item_type: str, x: float, y: float, **kwargs):
        """Create specific item instance

        Args:
            item_type (str): Type of item to create
            x, y (float): Position
            **kwargs: Additional arguments for item creation

        Returns:
            Item: New item instance or None if type unknown
        """
        # Check basic items first
        if item_type in cls._basic_item_registry:
            item_class = cls._basic_item_registry[item_type]

            if item_type == ItemType.WEAPON.value:
                # Need weapon_type for weapon pickup
                weapon_type = kwargs.get('weapon_type', cls._get_random_weapon_type())
                return item_class(x, y, weapon_type)
            else:
                return item_class(x, y, **kwargs)

        # Check powerups
        elif item_type in cls._powerup_registry:
            item_class = cls._powerup_registry[item_type]
            return item_class(x, y)

        else:
            print(f"Warning: Unknown item type '{item_type}'")
            return None

    @classmethod
    def create_random_basic_item(cls, x: float, y: float):
        """Create random basic item (health, ammo, weapon)

        Args:
            x, y (float): Position

        Returns:
            Item: Random basic item
        """
        item_type = cls._weighted_random_choice(cls._basic_item_weights)
        return cls.create_item(item_type, x, y)

    @classmethod
    def create_random_powerup(cls, x: float, y: float):
        """Create random powerup with rarity-based weights

        Args:
            x, y (float): Position

        Returns:
            Powerup: Random powerup
        """
        powerup_type = cls._weighted_random_choice(cls._powerup_weights)
        return cls.create_item(powerup_type, x, y)

    @classmethod
    def create_random_item(cls, x: float, y: float, powerup_chance=0.15):
        """Create random item (basic item or powerup)

        Args:
            x, y (float): Position
            powerup_chance (float): Chance of spawning powerup vs basic item

        Returns:
            Item: Random item
        """
        if random.random() < powerup_chance:
            return cls.create_random_powerup(x, y)
        else:
            return cls.create_random_basic_item(x, y)

    @classmethod
    def _weighted_random_choice(cls, weights_dict):
        """Choose random item based on weights

        Args:
            weights_dict (dict): Dict of {item_type: weight}

        Returns:
            str: Chosen item type
        """
        items = list(weights_dict.keys())
        weights = list(weights_dict.values())
        return random.choices(items, weights=weights, k=1)[0]

    @classmethod
    def _get_random_weapon_type(cls):
        """Get random weapon type based on weights

        Returns:
            str: Random weapon type
        """
        return random.choices(cls._weapon_types, weights=cls._weapon_weights, k=1)[0]

    @classmethod
    def get_all_item_types(cls):
        """Get list of all available item types

        Returns:
            list: List of all item type strings
        """
        return list(cls._basic_item_registry.keys()) + list(cls._powerup_registry.keys())

    @classmethod
    def get_basic_item_types(cls):
        """Get list of basic item types

        Returns:
            list: List of basic item type strings
        """
        return list(cls._basic_item_registry.keys())

    @classmethod
    def get_powerup_types(cls):
        """Get list of powerup types

        Returns:
            list: List of powerup type strings
        """
        return list(cls._powerup_registry.keys())

    @classmethod
    def is_powerup(cls, item_type: str):
        """Check if item type is a powerup

        Args:
            item_type (str): Item type to check

        Returns:
            bool: True if item is powerup
        """
        return item_type in cls._powerup_registry

    @classmethod
    def get_item_rarity(cls, item_type: str):
        """Get rarity of item type

        Args:
            item_type (str): Item type

        Returns:
            str: Rarity level or "common" if not powerup
        """
        if not cls.is_powerup(item_type):
            return ItemRarity.COMMON.value

        # Determine rarity based on spawn weight
        weight = cls._powerup_weights.get(item_type, 0)
        if weight <= 5:
            return ItemRarity.LEGENDARY.value
        elif weight <= 15:
            return ItemRarity.RARE.value
        else:
            return ItemRarity.COMMON.value


# ========================================
# CONVENIENCE FUNCTIONS (for easier use)
# ========================================

def create_random_item(x: float, y: float, powerup_chance=0.15):
    """Convenience function to create random item

    Args:
        x, y (float): Position
        powerup_chance (float): Chance of spawning powerup vs basic item

    Returns:
        Item: Random item
    """
    return ItemFactory.create_random_item(x, y, powerup_chance)


def create_random_powerup(x: float, y: float):
    """Convenience function to create random powerup

    Args:
        x, y (float): Position

    Returns:
        Powerup: Random powerup
    """
    return ItemFactory.create_random_powerup(x, y)


def create_health_pack(x: float, y: float, heal_amount=25):
    """Convenience function to create health pack

    Args:
        x, y (float): Position
        heal_amount (int): Amount of health to restore

    Returns:
        HealthPack: Health pack item
    """
    return ItemFactory.create_item(ItemType.HEALTH.value, x, y, heal_amount=heal_amount)


def create_ammo_pack(x: float, y: float, ammo_amount=30):
    """Convenience function to create ammo pack

    Args:
        x, y (float): Position
        ammo_amount (int): Amount of ammo to give

    Returns:
        AmmoPack: Ammo pack item
    """
    return ItemFactory.create_item(ItemType.AMMO.value, x, y, ammo_amount=ammo_amount)


def create_weapon_pickup(x: float, y: float, weapon_type=None):
    """Convenience function to create weapon pickup

    Args:
        x, y (float): Position
        weapon_type (str, optional): Specific weapon type or random if None

    Returns:
        WeaponPickup: Weapon pickup item
    """
    return ItemFactory.create_item(ItemType.WEAPON.value, x, y, weapon_type=weapon_type)


def create_powerup(x: float, y: float, powerup_type):
    """Convenience function to create specific powerup

    Args:
        x, y (float): Position
        powerup_type (str): Type of powerup to create

    Returns:
        Powerup: Powerup item
    """
    return ItemFactory.create_item(powerup_type, x, y)
