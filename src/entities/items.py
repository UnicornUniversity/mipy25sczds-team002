import pygame
import random
from entities.entity import Entity
from utils.constants import (
    ITEM_SIZE, HEALTH_PACK_COLOR, WEAPON_COLOR, POWERUP_COLOR,
    HEALTH_PACK_HEAL_AMOUNT,
    # Weapon colors for display
    PISTOL_BULLET_COLOR, SHOTGUN_BULLET_COLOR, ASSAULT_RIFLE_BULLET_COLOR,
    SNIPER_RIFLE_BULLET_COLOR, BAZOOKA_BULLET_COLOR
)
from utils.sprite_loader import get_texture, get_scaled_texture

class Item(Entity):
    """Base class for all pickable items"""

    def __init__(self, x, y, item_type, color):
        """Initialize the item

        Args:
            x (float): Initial x position
            y (float): Initial y position
            item_type (str): Type of item ('health', 'weapon', 'powerup')
            color (tuple): RGB color tuple
        """
        super().__init__(x, y, ITEM_SIZE, ITEM_SIZE, color)
        self.item_type = item_type
        self.picked_up = False

    def render(self, screen, camera_offset=(0, 0)):
        """Render the item using its sprite

        Args:
            screen (pygame.Surface): Screen to render on
            camera_offset (tuple): Camera offset (x, y)
        """
        if self.picked_up:
            return

        # Get the sprite for this item type
        sprite = self._get_sprite()

        if sprite:
            # Calculate position
            pos_x = self.rect.x - camera_offset[0]
            pos_y = self.rect.y - camera_offset[1]

            # Draw the sprite
            screen.blit(sprite, (pos_x, pos_y))
        else:
            # Fallback to drawing a circle if no sprite is available
            center_x = self.rect.x + self.width // 2 - camera_offset[0]
            center_y = self.rect.y + self.height // 2 - camera_offset[1]
            pygame.draw.circle(screen, self.color, (center_x, center_y), self.width // 2)

    def _get_sprite(self):
        """Get the sprite for this item type.

        Returns:
            pygame.Surface: The sprite surface, or None if not found
        """
        # This is a base method that should be overridden by subclasses
        return None

    def pickup(self, player):
        """Handle item pickup by player

        Args:
            player: The player that picked up the item

        Returns:
            str: Message to display
        """
        self.picked_up = True
        return f"Picked up {self.item_type}"

    @staticmethod
    def create_random_item(x, y, weapon_type=None):
        """Create a random item at the specified position

        Args:
            x (float): X position
            y (float): Y position
            weapon_type (str, optional): Specific weapon type to create, if None a random item is created

        Returns:
            Item: A random item (HealthPack or Weapon)
        """
        # If a specific weapon type is provided, create that weapon
        if weapon_type is not None:
            return Weapon(x, y, weapon_type)

        # Otherwise, randomly choose between health pack and weapon
        item_type = random.choice(['health', 'weapon'])

        if item_type == 'health':
            return HealthPack(x, y)
        else:
            # Randomly select a weapon type from the hierarchy
            # Lower tier weapons are more common
            weights = [0.5, 0.25, 0.15, 0.07, 0.03]  # Probabilities for each weapon tier
            weapon_type = random.choices(
                Weapon.WEAPON_HIERARCHY,
                weights=weights[:len(Weapon.WEAPON_HIERARCHY)],
                k=1
            )[0]
            return Weapon(x, y, weapon_type)

class HealthPack(Item):
    """Health pack item that restores player health"""

    def __init__(self, x, y):
        """Initialize the health pack

        Args:
            x (float): Initial x position
            y (float): Initial y position
        """
        super().__init__(x, y, 'health', HEALTH_PACK_COLOR)

    def _get_sprite(self):
        """Get the health pack sprite.

        Returns:
            pygame.Surface: The health pack sprite, or None if not found
        """
        # Try to get a health pack sprite from the texture atlas
        # First check if there's a dedicated health pack sprite
        sprite = get_texture('items', 'health_pack')
        if sprite is None:
            # If not, try to get a generic health sprite
            sprite = get_texture('items', 'health')

        return sprite

    def pickup(self, player):
        """Handle health pack pickup by player

        Args:
            player: The player that picked up the health pack

        Returns:
            str: Message to display
        """
        self.picked_up = True

        # Restore player health
        player.health = min(player.health + HEALTH_PACK_HEAL_AMOUNT, 100)

        return "Picked up Health Pack"

class Weapon(Item):
    """Weapon item that can be equipped by the player"""

    # Define weapon hierarchy (from lowest to highest)
    WEAPON_HIERARCHY = ["pistol", "shotgun", "assault_rifle", "sniper_rifle", "bazooka"]

    # Define weapon colors for display (used as fallback if sprite is not available)
    WEAPON_COLORS = {
        "pistol": PISTOL_BULLET_COLOR,
        "shotgun": SHOTGUN_BULLET_COLOR,
        "assault_rifle": ASSAULT_RIFLE_BULLET_COLOR,
        "sniper_rifle": SNIPER_RIFLE_BULLET_COLOR,
        "bazooka": BAZOOKA_BULLET_COLOR
    }

    # Map weapon types to sprite names
    WEAPON_SPRITE_NAMES = {
        "pistol": "pistol",
        "shotgun": "shotgun",
        "assault_rifle": "assault_rifle",
        "sniper_rifle": "sniper_rifle",
        "bazooka": "explosives"  # Bazooka uses the explosives sprite
    }

    def __init__(self, x, y, weapon_type="pistol"):
        """Initialize the weapon

        Args:
            x (float): Initial x position
            y (float): Initial y position
            weapon_type (str): Type of weapon to create ("pistol" by default)
        """
        # Use the weapon's specific color if available, otherwise use default WEAPON_COLOR
        color = self.WEAPON_COLORS.get(weapon_type, WEAPON_COLOR)
        super().__init__(x, y, 'weapon', color)
        self.weapon_type = weapon_type

    def _get_sprite(self):
        """Get the weapon sprite based on weapon type.

        Returns:
            pygame.Surface: The weapon sprite, or None if not found
        """
        # Get the sprite name for this weapon type
        sprite_name = self.WEAPON_SPRITE_NAMES.get(self.weapon_type, self.weapon_type)

        # Try to get the weapon sprite from the texture atlas
        sprite = get_texture('weapon', sprite_name)

        # Make weapon icons at least twice as large as the default ITEM_SIZE
        if sprite:
            # Use a fixed scale factor of 2.0 to make weapons larger
            scale_factor = 2.0
            sprite = get_scaled_texture('weapon', sprite_name, scale_factor)

        return sprite

    def pickup(self, player):
        """Handle weapon pickup by player

        Args:
            player: The player that picked up the weapon

        Returns:
            str: Message to display
        """
        self.picked_up = True

        # Import here to avoid circular imports
        from systems.weapons import Pistol, Shotgun, AssaultRifle, SniperRifle, Bazooka

        # Create the appropriate weapon based on weapon_type
        if self.weapon_type == "pistol":
            player.weapon = Pistol()
        elif self.weapon_type == "shotgun":
            player.weapon = Shotgun()
        elif self.weapon_type == "assault_rifle":
            player.weapon = AssaultRifle()
        elif self.weapon_type == "sniper_rifle":
            player.weapon = SniperRifle()
        elif self.weapon_type == "bazooka":
            player.weapon = Bazooka()
        else:
            # Default to pistol if weapon type is unknown
            player.weapon = Pistol()

        # Spawn a new weapon of the next tier
        from game.game_state import GameplayState
        if GameplayState.instance:
            GameplayState.instance.spawn_next_tier_weapon(self.weapon_type)

        return f"Picked up {self.weapon_type.replace('_', ' ').title()}"

    @staticmethod
    def get_next_tier_weapon(current_weapon_type):
        """Get the next tier weapon type based on the current weapon type

        Args:
            current_weapon_type (str): Current weapon type

        Returns:
            str: Next tier weapon type, or None if already at highest tier
        """
        try:
            current_index = Weapon.WEAPON_HIERARCHY.index(current_weapon_type)
            if current_index < len(Weapon.WEAPON_HIERARCHY) - 1:
                return Weapon.WEAPON_HIERARCHY[current_index + 1]
        except ValueError:
            # If weapon type not found in hierarchy, return first weapon
            return Weapon.WEAPON_HIERARCHY[0]

        # If already at highest tier, return None
        return None

class Powerup(Item):
    """Powerup item that provides temporary benefits"""

    def __init__(self, x, y):
        """Initialize the powerup

        Args:
            x (float): Initial x position
            y (float): Initial y position
        """
        super().__init__(x, y, 'powerup', POWERUP_COLOR)

    def _get_sprite(self):
        """Get the powerup sprite.

        Returns:
            pygame.Surface: The powerup sprite, or None if not found
        """
        # Try to get a powerup sprite from the texture atlas
        sprite = get_texture('items', 'powerup')

        # If the sprite is too large, scale it to fit the item size
        if sprite and (sprite.get_width() > ITEM_SIZE or sprite.get_height() > ITEM_SIZE):
            # Calculate scale factor to fit within ITEM_SIZE
            scale_factor = min(ITEM_SIZE / sprite.get_width(), ITEM_SIZE / sprite.get_height())
            sprite = get_scaled_texture('items', 'powerup', scale_factor)

        return sprite

    def pickup(self, player):
        """Handle powerup pickup by player

        Args:
            player: The player that picked up the powerup

        Returns:
            str: Message to display
        """
        self.picked_up = True

        # In a more complete implementation, this would apply a temporary effect to the player

        return "Picked up Powerup"
