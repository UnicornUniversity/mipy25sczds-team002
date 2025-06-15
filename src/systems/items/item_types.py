"""
Item Types Module - Base Item Classes and Enums
==============================================

Contains all basic item type definitions, enums, and base classes.
"""

import pygame
import math
from enum import Enum
from utils.constants import BLACK, WHITE, GREEN, BLUE, YELLOW, RED, PURPLE
from utils.sprite_loader import get_texture


class ItemType(Enum):
    """Enum pro typy itemů"""
    WEAPON = "weapon"
    HEALTH = "health"
    INFINITE_AMMO = "infinite_ammo"
    SPEED_BOOST = "speed_boost"
    DAMAGE_BOOST = "damage_boost"
    HEALTH_REGEN = "health_regen"
    INVINCIBILITY = "invincibility"
    RAPID_FIRE = "rapid_fire"


class ItemRarity(Enum):
    """Enum pro raritu itemů"""
    COMMON = "common"
    RARE = "rare"
    LEGENDARY = "legendary"


class Item:
    """Base class pro všechny item typy"""

    def __init__(self, x, y, item_type=ItemType.HEALTH, rarity=ItemRarity.COMMON):
        """Initialize item

        Args:
            x, y (float): Position
            item_type (ItemType): Type of item
            rarity (ItemRarity): Item rarity
        """
        self.x = x
        self.y = y
        self.item_type = item_type
        self.rarity = rarity
        self.rect = pygame.Rect(x, y, 32, 32)  # Standard item size
        self.collected = False
        self.sprite = None
        self.color = self._get_rarity_color()
        self.is_expired = False

        # Animation
        self.bob_time = 0
        self.bob_height = 8
        self.bob_speed = 3


    def _get_rarity_color(self):
        """Get color based on rarity"""
        color_map = {
            ItemRarity.COMMON: WHITE,
            ItemRarity.RARE: BLUE,
            ItemRarity.LEGENDARY: PURPLE
        }
        return color_map.get(self.rarity, WHITE)

    def update(self, dt):
        """Update item (animation, etc.)"""
        self.bob_time += dt

    def render(self, screen, camera_offset=(0, 0)):
        """Render the item"""
        # Calculate screen position with camera offset
        screen_x = self.rect.x - camera_offset[0]
        screen_y = self.rect.y - camera_offset[1]

        # Add bobbing animation
        bob_offset = math.sin(self.bob_time * self.bob_speed) * self.bob_height
        render_y = screen_y + bob_offset

        if self.sprite:
            screen.blit(self.sprite, (screen_x, render_y))
        else:
            # Fallback rectangle rendering
            pygame.draw.rect(screen, self.color, (screen_x, render_y, self.rect.width, self.rect.height))

    def collect(self, player):
        """Collect the item - to be overridden by subclasses

        Args:
            player: Player who collected the item

        Returns:
            bool: True if item was successfully collected
        """
        self.collected = True
        return True

    def is_collected(self):
        """Check if item has been collected"""
        return self.collected

class WeaponPickup(Item):
    """Weapon pickup item"""

    def __init__(self, x, y, weapon_type="pistol"):
        """Initialize weapon pickup

        Args:
            x, y (float): Position
            weapon_type (str): Type of weapon to give
        """
        super().__init__(x, y, ItemType.WEAPON, ItemRarity.RARE)
        self.weapon_type = weapon_type
        self.color = YELLOW
        self.is_expired = False
        self._load_sprite()

    def _load_sprite(self):
        """Load weapon sprite"""
        sprite = get_texture("weapon", self.weapon_type)
        if sprite:
            # Scale weapon sprite by a factor of 2 to make it larger on the game field
            original_width, original_height = sprite.get_size()
            self.sprite = pygame.transform.scale(sprite, (original_width * 2, original_height * 2))
        else:
            self.sprite = None

    def collect(self, player):
        """Give weapon to player"""
        print("Collected weapon")
        if not self.collected:
            from systems.weapons import WeaponFactory
            weapon = WeaponFactory.create_weapon(self.weapon_type)
            if weapon and player.add_weapon(weapon):
                self.collected = True
                return True
        return False


class HealthPack(Item):
    """Health restoration item"""

    def __init__(self, x, y, heal_amount=25):
        """Initialize health pack

        Args:
            x, y (float): Position
            heal_amount (int): Amount of health to restore
        """
        super().__init__(x, y, ItemType.HEALTH, ItemRarity.COMMON)
        self.heal_amount = heal_amount
        self.color = GREEN
        self._load_sprite()

    def _load_sprite(self):
        """Load health pack sprite"""
        sprite = get_texture("pickups", "health")
        if sprite:
            # Resize to 32x32 to match collision rect
            self.sprite = pygame.transform.scale(sprite, (32, 32))
        else:
            print("Warning: Could not load health pack sprite")
            self.sprite = None

    def collect(self, player):
        """Heal the player"""
        if not self.collected and player.health < player.max_health:
            print("Collected health pack!")
            player.heal(self.heal_amount)
            self.collected = True
            return True

        return False


class InfiniteAmmoPack(Item):
    """Infinite ammunition item"""

    def __init__(self, x, y, duration=15.0):
        """Initialize infinite ammo pack

        Args:
            x, y (float): Position
            duration (float): Duration in seconds
        """
        super().__init__(x, y, ItemType.INFINITE_AMMO, ItemRarity.COMMON)
        self.duration = duration
        self.color = BLUE
        self._load_sprite()

    def _load_sprite(self):
        """Load infinite ammo pack sprite"""
        sprite = get_texture("pickups", "ammo")
        if sprite:
            # Resize to 32x32 to match collision rect
            self.sprite = pygame.transform.scale(sprite, (32, 32))
        else:
            print("Warning: Could not load infinite ammo pack sprite")
            self.sprite = None

    def collect(self, player):
        """Give infinite ammo to player"""
        print("Collected infinite ammo pack!")
        if not self.collected:
            # Apply infinite ammo effect
            from systems.items.item_effects import apply_item_effect
            apply_item_effect(player, "infinite_ammo", self.duration, True)

            # Also fill current weapon's ammo
            current_weapon = player.get_current_weapon()
            if current_weapon:
                current_weapon.ammo = current_weapon.magazine_size

            self.collected = True
            return True
        return False


class Powerup(Item):
    """Base class for all powerups"""

    def __init__(self, x, y, powerup_type, duration=10.0, rarity=ItemRarity.RARE):
        """Initialize powerup

        Args:
            x, y (float): Position
            powerup_type (ItemType): Type of powerup
            duration (float): Duration in seconds
            rarity (ItemRarity): Powerup rarity
        """
        super().__init__(x, y, powerup_type, rarity)
        self.duration = duration
        self.effect_applied = False
        self._load_sprite()

    def _load_sprite(self):
        """Load powerup sprite based on item type"""
        # Map powerup types to sprite names
        sprite_mapping = {
            ItemType.SPEED_BOOST.value: "more_speed",
            ItemType.DAMAGE_BOOST.value: "more_damage",
            ItemType.HEALTH_REGEN.value: "regeneration",
            ItemType.INVINCIBILITY.value: "invincibility",
            ItemType.RAPID_FIRE.value: "ammo"  # Using ammo sprite for rapid fire
        }

        sprite_name = sprite_mapping.get(self.item_type)
        if sprite_name:
            sprite = get_texture("pickups", sprite_name)
            if sprite:
                # Resize to 32x32 to match collision rect
                self.sprite = pygame.transform.scale(sprite, (32, 32))
            else:
                print(f"Warning: Could not load powerup sprite: {sprite_name}")
                self.sprite = None

    def collect(self, player):
        """Apply powerup effect to player"""
        print(f"Collected {self.item_type.value} powerup!")
        if not self.collected:
            self.apply_effect(player)
            self.collected = True
            return True
        return False

    def apply_effect(self, player):
        """Apply the powerup effect - to be overridden"""
        pass



class SpeedBoost(Powerup):
    """Speed boost powerup"""

    def __init__(self, x, y, speed_multiplier=1.5, duration=15.0):
        """Initialize speed boost

        Args:
            x, y (float): Position
            speed_multiplier (float): Speed multiplication factor
            duration (float): Duration in seconds
        """
        super().__init__(x, y, ItemType.SPEED_BOOST, duration, ItemRarity.COMMON)
        self.speed_multiplier = speed_multiplier
        self.color = YELLOW

    def _load_sprite(self):
        """Load speed boost sprite"""
        sprite = get_texture("pickups", "more_speed")
        if sprite:
            # Resize to 32x32 to match collision rect
            self.sprite = pygame.transform.scale(sprite, (32, 32))
        else:
            print("Warning: Could not load speed boost sprite")
            self.sprite = None

    def apply_effect(self, player):
        """Apply speed boost to player"""
        from systems.items.item_effects import apply_item_effect
        apply_item_effect(player, "speed_boost", self.duration, self.speed_multiplier)
        print(f"Speed boost applied! ({self.speed_multiplier}x for {self.duration}s)")


class DamageBoost(Powerup):
    """Damage boost powerup"""

    def __init__(self, x, y, damage_multiplier=2.0, duration=10.0):
        """Initialize damage boost

        Args:
            x, y (float): Position
            damage_multiplier (float): Damage multiplication factor
            duration (float): Duration in seconds
        """
        super().__init__(x, y, ItemType.DAMAGE_BOOST, duration, ItemRarity.RARE)
        self.damage_multiplier = damage_multiplier
        self.color = RED

    def _load_sprite(self):
        """Load damage boost sprite"""
        sprite = get_texture("pickups", "more_damage")
        if sprite:
            # Resize to 32x32 to match collision rect
            self.sprite = pygame.transform.scale(sprite, (32, 32))
        else:
            print("Warning: Could not load damage boost sprite")
            self.sprite = None

    def apply_effect(self, player):
        """Apply damage boost to player"""
        from systems.items.item_effects import apply_item_effect
        apply_item_effect(player, "damage_boost", self.duration, self.damage_multiplier)
        print(f"Damage boost applied! ({self.damage_multiplier}x for {self.duration}s)")


class HealthRegeneration(Powerup):
    """Health regeneration powerup"""

    def __init__(self, x, y, regen_rate=2, duration=20.0):
        """Initialize health regeneration

        Args:
            x, y (float): Position
            regen_rate (int): Health points regenerated per second
            duration (float): Duration in seconds
        """
        super().__init__(x, y, ItemType.HEALTH_REGEN, duration, ItemRarity.RARE)
        self.regen_rate = regen_rate
        self.color = GREEN

    def _load_sprite(self):
        """Load health regeneration sprite"""
        sprite = get_texture("pickups", "regeneration")
        if sprite:
            # Resize to 32x32 to match collision rect
            self.sprite = pygame.transform.scale(sprite, (32, 32))
        else:
            print("Warning: Could not load health regeneration sprite")
            self.sprite = None

    def apply_effect(self, player):
        """Apply health regeneration to player"""
        from systems.items.item_effects import apply_item_effect
        apply_item_effect(player, "health_regen", self.duration, self.regen_rate)
        print(f"Health regeneration applied! ({self.regen_rate} HP/s for {self.duration}s)")


class Invincibility(Powerup):
    """Invincibility powerup"""

    def __init__(self, x, y, duration=5.0):
        """Initialize invincibility

        Args:
            x, y (float): Position
            duration (float): Duration in seconds
        """
        super().__init__(x, y, ItemType.INVINCIBILITY, duration, ItemRarity.LEGENDARY)
        self.color = PURPLE

    def _load_sprite(self):
        """Load invincibility sprite"""
        sprite = get_texture("pickups", "invincibility")
        if sprite:
            # Resize to 32x32 to match collision rect
            self.sprite = pygame.transform.scale(sprite, (32, 32))
        else:
            print("Warning: Could not load invincibility sprite")
            self.sprite = None

    def apply_effect(self, player):
        """Apply invincibility to player"""
        from systems.items.item_effects import apply_item_effect
        apply_item_effect(player, "invincibility", self.duration, True)
        print(f"Invincibility applied! ({self.duration}s)")


class RapidFire(Powerup):
    """Rapid fire powerup"""

    def __init__(self, x, y, fire_rate_multiplier=3.0, duration=8.0):
        """Initialize rapid fire

        Args:
            x, y (float): Position
            fire_rate_multiplier (float): Fire rate multiplication factor
            duration (float): Duration in seconds
        """
        super().__init__(x, y, ItemType.RAPID_FIRE, duration, ItemRarity.RARE)
        self.fire_rate_multiplier = fire_rate_multiplier
        self.color = BLUE

    def _load_sprite(self):
        """Load rapid fire sprite"""
        sprite = get_texture("pickups", "ammo")  # Using ammo sprite for rapid fire
        if sprite:
            # Resize to 32x32 to match collision rect
            self.sprite = pygame.transform.scale(sprite, (32, 32))
        else:
            print("Warning: Could not load rapid fire sprite")
            self.sprite = None

    def apply_effect(self, player):
        """Apply rapid fire to player"""
        from systems.items.item_effects import apply_item_effect
        apply_item_effect(player, "rapid_fire", self.duration, self.fire_rate_multiplier)
        print(f"Rapid fire applied! ({self.fire_rate_multiplier}x for {self.duration}s)")