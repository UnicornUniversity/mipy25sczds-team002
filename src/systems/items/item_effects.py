"""
Item Effects - Powerup Effect Management System
==============================================

Systém pro správu temporary effects na playerovi způsobených powerupy.
"""

import pygame
from typing import Dict, List, Any


class Effect:
    """Single effect instance"""

    def __init__(self, effect_type: str, duration: float, value: Any, start_time: float = None):
        """Initialize effect

        Args:
            effect_type (str): Type of effect
            duration (float): Duration in seconds
            value (Any): Effect value/parameter
            start_time (float): Start time (defaults to current time)
        """
        self.effect_type = effect_type
        self.duration = duration
        self.value = value
        self.start_time = start_time or pygame.time.get_ticks() / 1000.0
        self.active = True

    def update(self, dt: float):
        """Update effect (check expiration)"""
        current_time = pygame.time.get_ticks() / 1000.0
        if current_time - self.start_time >= self.duration:
            self.active = False

    def is_active(self):
        """Check if effect is still active"""
        return self.active

    def get_remaining_time(self):
        """Get remaining time in seconds"""
        current_time = pygame.time.get_ticks() / 1000.0
        remaining = self.duration - (current_time - self.start_time)
        return max(0, remaining)


class EffectManager:
    """Manages all active effects on an entity"""

    def __init__(self):
        """Initialize effect manager"""
        self.effects: Dict[str, Effect] = {}
        self.effect_history: List[str] = []  # For logging/debug

    def add_effect(self, effect_type: str, duration: float, value: Any):
        """Add or refresh an effect

        Args:
            effect_type (str): Type of effect
            duration (float): Duration in seconds
            value (Any): Effect value
        """
        # If effect already exists, refresh duration
        if effect_type in self.effects:
            self.effects[effect_type].duration = duration
            self.effects[effect_type].start_time = pygame.time.get_ticks() / 1000.0
            self.effects[effect_type].value = value
            self.effects[effect_type].active = True
        else:
            # Create new effect
            self.effects[effect_type] = Effect(effect_type, duration, value)

        self.effect_history.append(effect_type)
        print(f"Effect applied: {effect_type} for {duration}s")

    def remove_effect(self, effect_type: str):
        """Remove specific effect

        Args:
            effect_type (str): Effect type to remove
        """
        if effect_type in self.effects:
            del self.effects[effect_type]
            print(f"Effect removed: {effect_type}")

    def update(self, dt: float):
        """Update all effects (remove expired ones)"""
        expired_effects = []

        for effect_type, effect in self.effects.items():
            effect.update(dt)
            if not effect.is_active():
                expired_effects.append(effect_type)

        # Remove expired effects
        for effect_type in expired_effects:
            self.remove_effect(effect_type)

    def has_effect(self, effect_type: str):
        """Check if specific effect is active

        Args:
            effect_type (str): Effect type to check

        Returns:
            bool: True if effect is active
        """
        return effect_type in self.effects and self.effects[effect_type].is_active()

    def get_effect_value(self, effect_type: str, default=None):
        """Get value of specific effect

        Args:
            effect_type (str): Effect type
            default: Default value if effect not active

        Returns:
            Any: Effect value or default
        """
        if self.has_effect(effect_type):
            return self.effects[effect_type].value
        return default

    def get_effect_remaining_time(self, effect_type: str):
        """Get remaining time for specific effect

        Args:
            effect_type (str): Effect type

        Returns:
            float: Remaining time in seconds or 0 if not active
        """
        if self.has_effect(effect_type):
            return self.effects[effect_type].get_remaining_time()
        return 0

    def get_all_active_effects(self):
        """Get list of all active effect types

        Returns:
            list: List of active effect type strings
        """
        return [effect_type for effect_type, effect in self.effects.items() if effect.is_active()]

    def clear_all_effects(self):
        """Remove all effects"""
        self.effects.clear()
        print("All effects cleared")

    def get_effect_info(self):
        """Get effect information for UI display

        Returns:
            dict: Effect information
        """
        active_effects = {}
        for effect_type, effect in self.effects.items():
            if effect.is_active():
                active_effects[effect_type] = {
                    'remaining_time': effect.get_remaining_time(),
                    'value': effect.value,
                    'duration': effect.duration
                }

        return active_effects

    # === CONVENIENCE METHODS FOR COMMON EFFECTS ===

    def get_speed_multiplier(self):
        """Get current speed multiplier from effects"""
        base_multiplier = 1.0
        if self.has_effect("speed_boost"):
            base_multiplier *= self.get_effect_value("speed_boost", 1.0)
        return base_multiplier

    def get_damage_multiplier(self):
        """Get current damage multiplier from effects"""
        base_multiplier = 1.0
        if self.has_effect("damage_boost"):
            base_multiplier *= self.get_effect_value("damage_boost", 1.0)
        return base_multiplier

    def get_fire_rate_multiplier(self):
        """Get current fire rate multiplier from effects"""
        base_multiplier = 1.0
        if self.has_effect("rapid_fire"):
            base_multiplier *= self.get_effect_value("rapid_fire", 1.0)
        return base_multiplier

    def is_invincible(self):
        """Check if entity is invincible"""
        return self.has_effect("invincibility")

    def has_explosive_ammo(self):
        """Check if entity has explosive ammo"""
        return self.has_effect("explosive_ammo")

    def get_health_regen_rate(self):
        """Get health regeneration rate"""
        return self.get_effect_value("health_regen", 0)


# ========================================
# GLOBAL CONVENIENCE FUNCTIONS
# ========================================

# Base effect classes for backward compatibility
ItemEffect = Effect
HealthEffect = Effect
AmmoEffect = Effect
WeaponEffect = Effect
StatBoostEffect = Effect
TemporaryEffect = Effect


def apply_item_effect(entity, effect_type: str, duration: float, value: Any):
    """Apply effect to entity

    Args:
        entity: Entity to apply effect to
        effect_type (str): Type of effect
        duration (float): Duration in seconds
        value (Any): Effect value
    """
    if hasattr(entity, 'effect_manager'):
        entity.effect_manager.add_effect(effect_type, duration, value)
    else:
        print(f"Warning: Entity has no effect_manager, cannot apply {effect_type}")


def remove_effect(entity, effect_type: str):
    """Remove effect from entity

    Args:
        entity: Entity to remove effect from
        effect_type (str): Effect type to remove
    """
    if hasattr(entity, 'effect_manager'):
        entity.effect_manager.remove_effect(effect_type)
    else:
        print(f"Warning: Entity has no effect_manager, cannot remove {effect_type}")