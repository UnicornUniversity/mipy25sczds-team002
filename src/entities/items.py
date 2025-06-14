import pygame
import random
from entities.entity import Entity
from utils.constants import (
    ITEM_SIZE, HEALTH_PACK_COLOR, WEAPON_COLOR, POWERUP_COLOR,
    HEALTH_PACK_HEAL_AMOUNT
)

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
        """Render the item as a circle

        Args:
            screen (pygame.Surface): Screen to render on
            camera_offset (tuple): Camera offset (x, y)
        """
        if self.picked_up:
            return

        # Calculate center position
        center_x = self.rect.x + self.width // 2 - camera_offset[0]
        center_y = self.rect.y + self.height // 2 - camera_offset[1]

        # Draw item as a circle
        pygame.draw.circle(screen, self.color, (center_x, center_y), self.width // 2)

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
    def create_random_item(x, y):
        """Create a random item at the specified position

        Args:
            x (float): X position
            y (float): Y position

        Returns:
            Item: A random item (HealthPack or Weapon)
        """
        item_type = random.choice(['health', 'weapon'])

        if item_type == 'health':
            return HealthPack(x, y)
        else:
            return Weapon(x, y, "pistol")

class HealthPack(Item):
    """Health pack item that restores player health"""

    def __init__(self, x, y):
        """Initialize the health pack

        Args:
            x (float): Initial x position
            y (float): Initial y position
        """
        super().__init__(x, y, 'health', HEALTH_PACK_COLOR)

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

    def __init__(self, x, y, weapon_type="pistol"):
        """Initialize the weapon

        Args:
            x (float): Initial x position
            y (float): Initial y position
            weapon_type (str): Type of weapon to create ("pistol" by default)
        """
        super().__init__(x, y, 'weapon', WEAPON_COLOR)
        self.weapon_type = weapon_type

    def pickup(self, player):
        """Handle weapon pickup by player

        Args:
            player: The player that picked up the weapon

        Returns:
            str: Message to display
        """
        self.picked_up = True

        # Import here to avoid circular imports
        from systems.weapons import Pistol

        # Create the appropriate weapon based on weapon_type
        if self.weapon_type == "pistol":
            player.weapon = Pistol()

        return f"Picked up {self.weapon_type.capitalize()}"

class Powerup(Item):
    """Powerup item that provides temporary benefits"""

    def __init__(self, x, y):
        """Initialize the powerup

        Args:
            x (float): Initial x position
            y (float): Initial y position
        """
        super().__init__(x, y, 'powerup', POWERUP_COLOR)

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
