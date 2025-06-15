class WeaponInventory:
    """Player-specific weapon inventory management

    Tento systém je navržen specificky pro hráče a spravuje:
    - Inventář zbraní (slots)
    - Přepínání mezi zbraněmi
    - Auto-switch logiku na základě weapon hierarchy
    - Weapon tier comparison
    """

    # Weapon hierarchy (from weakest to strongest)
    WEAPON_HIERARCHY = ["pistol", "shotgun", "sniper_rifle", "assault_rifle", "bazooka"]

    def __init__(self, max_weapons=5):
        """Initialize weapon inventory

        Args:
            max_weapons (int): Maximum number of weapons player can carry
        """
        self.weapons = [None] * max_weapons
        self.current_slot = 0
        self.max_weapons = max_weapons

    def add_weapon(self, weapon, auto_switch=True):
        """Add weapon to inventory

        Args:
            weapon: Weapon instance to add
            auto_switch (bool): Whether to automatically switch to better weapon

        Returns:
            bool: True if weapon was added successfully
        """
        # Find first empty slot
        for i in range(self.max_weapons):
            if self.weapons[i] is None:
                self.weapons[i] = weapon

                if auto_switch:
                    self._auto_switch_to_better_weapon(i)

                return True

        # Inventory full
        return False

    def switch_weapon(self, slot):
        """Switch to weapon in specified slot

        Args:
            slot (int): Weapon slot index (0-4)

        Returns:
            bool: True if switch was successful
        """
        if 0 <= slot < self.max_weapons and self.weapons[slot] is not None:
            self.current_slot = slot
            return True
        return False

    def get_current_weapon(self):
        """Get currently equipped weapon

        Returns:
            Weapon or None: Current weapon instance
        """
        if 0 <= self.current_slot < self.max_weapons:
            return self.weapons[self.current_slot]
        return None

    def get_weapon_at_slot(self, slot):
        """Get weapon at specific slot

        Args:
            slot (int): Slot index

        Returns:
            Weapon or None: Weapon at slot or None if empty
        """
        if 0 <= slot < self.max_weapons:
            return self.weapons[slot]
        return None

    def get_all_weapons(self):
        """Get list of all weapons in inventory

        Returns:
            list: List of weapons (may contain None for empty slots)
        """
        return self.weapons.copy()

    def get_weapon_count(self):
        """Get number of weapons in inventory

        Returns:
            int: Number of weapons currently in inventory
        """
        return sum(1 for weapon in self.weapons if weapon is not None)

    def is_full(self):
        """Check if inventory is full

        Returns:
            bool: True if inventory is full
        """
        return self.get_weapon_count() >= self.max_weapons

    def remove_weapon(self, slot):
        """Remove weapon from specified slot

        Args:
            slot (int): Slot to clear

        Returns:
            Weapon or None: Removed weapon or None if slot was empty
        """
        if 0 <= slot < self.max_weapons:
            weapon = self.weapons[slot]
            self.weapons[slot] = None

            # If we removed current weapon, switch to first available
            if slot == self.current_slot:
                self._switch_to_first_available()

            return weapon
        return None

    def _auto_switch_to_better_weapon(self, new_weapon_slot):
        """Auto-switch to better weapon based on hierarchy

        Args:
            new_weapon_slot (int): Slot of newly added weapon
        """
        current_weapon = self.get_current_weapon()
        new_weapon = self.weapons[new_weapon_slot]

        if current_weapon is None:
            # No current weapon, switch to new one
            self.current_slot = new_weapon_slot
            return

        # Compare weapon tiers
        current_tier = self._get_weapon_tier(current_weapon)
        new_tier = self._get_weapon_tier(new_weapon)

        if new_tier > current_tier:
            self.current_slot = new_weapon_slot

    def _get_weapon_tier(self, weapon):
        """Get weapon tier based on hierarchy

        Args:
            weapon: Weapon instance

        Returns:
            int: Weapon tier (higher = better)
        """
        if weapon is None:
            return -1

        weapon_type = weapon.get_weapon_type()
        try:
            return self.WEAPON_HIERARCHY.index(weapon_type)
        except ValueError:
            # Unknown weapon type, assign lowest tier
            return 0

    def _switch_to_first_available(self):
        """Switch to first available weapon"""
        for i in range(self.max_weapons):
            if self.weapons[i] is not None:
                self.current_slot = i
                return

        # No weapons available
        self.current_slot = 0

    def cycle_weapon_forward(self):
        """Cycle to next weapon in inventory

        Returns:
            bool: True if switched to different weapon
        """
        start_slot = self.current_slot

        for i in range(1, self.max_weapons):
            next_slot = (self.current_slot + i) % self.max_weapons
            if self.weapons[next_slot] is not None:
                self.current_slot = next_slot
                return True

        return False

    def cycle_weapon_backward(self):
        """Cycle to previous weapon in inventory

        Returns:
            bool: True if switched to different weapon
        """
        start_slot = self.current_slot

        for i in range(1, self.max_weapons):
            prev_slot = (self.current_slot - i) % self.max_weapons
            if self.weapons[prev_slot] is not None:
                self.current_slot = prev_slot
                return True

        return False

    def get_inventory_status(self):
        """Get inventory status for UI display

        Returns:
            dict: Inventory information for HUD
        """
        return {
            'weapons': [
                {
                    'name': weapon.name if weapon else None,
                    'ammo': weapon.ammo if weapon else 0,
                    'magazine_size': weapon.magazine_size if weapon else 0,
                    'is_reloading': weapon.is_reloading if weapon else False
                }
                for weapon in self.weapons
            ],
            'current_slot': self.current_slot,
            'weapon_count': self.get_weapon_count(),
            'is_full': self.is_full()
        }