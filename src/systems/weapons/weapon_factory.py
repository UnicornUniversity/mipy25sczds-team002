from enum import Enum
from .weapon_types import Pistol, Shotgun, AssaultRifle, SniperRifle, Bazooka


class WeaponType(Enum):
    """Enum pro typy zbraní - zajišťuje type safety"""
    PISTOL = "pistol"
    SHOTGUN = "shotgun"
    ASSAULT_RIFLE = "assault_rifle"
    SNIPER_RIFLE = "sniper_rifle"
    BAZOOKA = "bazooka"


class WeaponFactory:
    """Factory pro vytváření weapon instancí

    Centralizuje vytváření zbraní a zajišťuje konzistentní API
    pro vytváření weapons napříč celou aplikací.
    """

    _weapon_registry = {
        WeaponType.PISTOL.value: Pistol,
        WeaponType.SHOTGUN.value: Shotgun,
        WeaponType.ASSAULT_RIFLE.value: AssaultRifle,
        WeaponType.SNIPER_RIFLE.value: SniperRifle,
        WeaponType.BAZOOKA.value: Bazooka,
    }

    @classmethod
    def create_weapon(cls, weapon_type: str):
        """Vytvoří weapon instance podle typu

        Args:
            weapon_type (str): Type of weapon to create

        Returns:
            Weapon: New weapon instance

        Raises:
            ValueError: If weapon_type is not supported
        """
        weapon_class = cls._weapon_registry.get(weapon_type)

        if weapon_class is None:
            # Fallback to pistol for unknown types (defensive programming)
            print(f"Warning: Unknown weapon type '{weapon_type}', falling back to pistol")
            weapon_class = Pistol

        return weapon_class()

    @classmethod
    def get_available_types(cls):
        """Get list of all available weapon types

        Returns:
            list: List of available weapon type strings
        """
        return list(cls._weapon_registry.keys())

    @classmethod
    def is_valid_type(cls, weapon_type: str):
        """Check if weapon type is valid

        Args:
            weapon_type (str): Weapon type to check

        Returns:
            bool: True if weapon type is supported
        """
        return weapon_type in cls._weapon_registry

    @classmethod
    def register_weapon_type(cls, weapon_type: str, weapon_class):
        """Register new weapon type (for extensibility)

        Args:
            weapon_type (str): New weapon type identifier
            weapon_class: Weapon class to register
        """
        cls._weapon_registry[weapon_type] = weapon_class