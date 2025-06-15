"""
Sprite Loader - Centralized Art Asset Management System
=======================================================

This module provides a comprehensive system for loading, optimizing, and managing
all art assets in the game. Ensures visual consistency and performance optimization.
Implements a texture atlas for efficient sprite management.
"""

import pygame
import os
from typing import Dict, Tuple, Optional, List, Any, Set
from utils.constants import TILE_SIZE, SPRITE_SIZE, SPRITE_GAP, SPRITESHEET_COLS, SPRITESHEET_ROWS, PLAYER_SIZE, \
    ITEM_SIZE


class TextureAtlas:
    """
    Texture Atlas for organizing and efficiently accessing game sprites.
    Groups sprites by category and provides a unified interface.
    """

    def __init__(self):
        self._textures: Dict[str, Dict[str, pygame.Surface]] = {}
        self._categories: Set[str] = set()

    def add_texture(self, category: str, name: str, texture: pygame.Surface) -> None:
        """Add a texture to the atlas.

        Args:
            category (str): Category of the texture (e.g., 'weapon', 'player')
            name (str): Name of the texture
            texture (pygame.Surface): The texture surface
        """
        if category not in self._textures:
            self._textures[category] = {}
            self._categories.add(category)

        self._textures[category][name] = texture

    def get_texture(self, category: str, name: str) -> Optional[pygame.Surface]:
        """Get a texture from the atlas.

        Args:
            category (str): Category of the texture
            name (str): Name of the texture

        Returns:
            Optional[pygame.Surface]: The texture surface, or None if not found
        """
        if category not in self._textures or name not in self._textures[category]:
            return None

        return self._textures[category][name]

    def get_categories(self) -> List[str]:
        """Get all texture categories.

        Returns:
            List[str]: List of all texture categories
        """
        return list(self._categories)

    def get_textures_in_category(self, category: str) -> List[str]:
        """Get all texture names in a category.

        Args:
            category (str): Category to get textures from

        Returns:
            List[str]: List of texture names in the category
        """
        if category not in self._textures:
            return []

        return list(self._textures[category].keys())

    def get_all_textures(self) -> Dict[str, Dict[str, pygame.Surface]]:
        """Get all textures in the atlas.

        Returns:
            Dict[str, Dict[str, pygame.Surface]]: All textures organized by category
        """
        return self._textures


class AssetManager:
    """
    Centralized manager for all game art assets.
    Handles loading, caching, and optimization of sprites and textures.
    Uses a texture atlas for efficient sprite management.
    """

    def __init__(self):
        self._sprites: Dict[str, pygame.Surface] = {}
        self._spritesheets: Dict[str, pygame.Surface] = {}
        self._texture_atlas = TextureAtlas()
        self._loaded = False
        self._missing_texture_color = (255, 0, 255)  # Pink color for missing textures

        # Asset paths
        self.assets_root = os.path.join(os.path.dirname(__file__), '..', '..', 'assets')
        self.images_path = os.path.join(self.assets_root, 'images')
        self.spritesheets_path = os.path.join(self.images_path, 'spritesheets')
        self.sprites_path = os.path.join(self.images_path, 'sprites')

    def load_all_assets(self) -> None:
        """Load all game assets and optimize them for performance."""
        if self._loaded:
            return

        print("Loading art assets...")

        # Load spritesheets first
        self._load_spritesheets()

        # Load individual sprites
        self._load_individual_sprites()

        # Apply performance optimizations
        self._optimize_surfaces()

        # Create fallback sprites if needed
        self._create_fallback_sprites()

        # For backward compatibility, copy all textures to the _sprites dictionary
        self._copy_textures_to_sprites()

        self._loaded = True
        print(f"Asset loading complete. Loaded {len(self._sprites)} sprites and {sum(len(textures) for textures in self._texture_atlas.get_all_textures().values())} textures in the atlas.")

    def _load_spritesheets(self) -> None:
        """Load and process spritesheet files."""
        spritesheet_files = [
            'spritesheet_characters.png',
            'spritesheet_tiles.png'
        ]

        for filename in spritesheet_files:
            filepath = os.path.join(self.spritesheets_path, filename)
            if os.path.exists(filepath):
                print(f"Loading spritesheet: {filename}")
                surface = pygame.image.load(filepath).convert_alpha()
                self._spritesheets[filename] = surface

                # Extract individual sprites from spritesheet
                self._extract_sprites_from_sheet(filename, surface)

    def _extract_sprites_from_sheet(self, sheet_name: str, surface: pygame.Surface) -> None:
        """Extract individual sprites from a spritesheet."""
        if sheet_name == '../assets/images/spritesheets/spritesheet_characters.png':
            self._extract_character_sprites(surface)
        elif sheet_name == 'spritesheet_tiles.png':
            self._extract_tile_sprites(surface)

    def _extract_character_sprites(self, surface: pygame.Surface) -> None:
        """Extract character sprites from character spritesheet.

        The spritesheet has the following format:
        - Each sprite is SPRITE_SIZE x SPRITE_SIZE (64x64)
        - There is a SPRITE_GAP (4 pixels) between sprites
        - The spritesheet has SPRITESHEET_COLS columns and SPRITESHEET_ROWS rows
        """
        # Define character types to extract with category mapping
        character_sprites = [
            ('player', 'idle'), ('player', 'walk_1'), ('player', 'walk_2'), ('player', 'walk_3'),
            ('zombie', 'basic_1'), ('zombie', 'basic_2'), ('zombie', 'runner_1'), ('zombie', 'runner_2'),
            ('zombie', 'tank_1'), ('zombie', 'tank_2')
        ]

        sprite_index = 0
        for row in range(min(SPRITESHEET_ROWS, len(character_sprites))):
            for col in range(min(SPRITESHEET_COLS, len(character_sprites) - sprite_index)):
                if sprite_index < len(character_sprites):
                    # Calculate position with gaps
                    x = col * (SPRITE_SIZE + SPRITE_GAP)
                    y = row * (SPRITE_SIZE + SPRITE_GAP)

                    # Extract sprite from spritesheet
                    sprite_rect = pygame.Rect(x, y, SPRITE_SIZE, SPRITE_SIZE)
                    sprite_surface = surface.subsurface(sprite_rect).copy()

                    # Scale to PLAYER_SIZE if needed
                    if SPRITE_SIZE != PLAYER_SIZE:
                        sprite_surface = pygame.transform.scale(sprite_surface, (PLAYER_SIZE, PLAYER_SIZE))

                    # Store sprite in texture atlas
                    category, name = character_sprites[sprite_index]
                    self._texture_atlas.add_texture(category, name, sprite_surface)

                    # For backward compatibility
                    legacy_name = f"{category}_{name}"
                    self._sprites[legacy_name] = sprite_surface

                    sprite_index += 1

    def _extract_tile_sprites(self, surface: pygame.Surface) -> None:
        """Extract environment tiles from tile spritesheet.

        The spritesheet has the following format:
        - Each sprite is SPRITE_SIZE x SPRITE_SIZE (64x64)
        - There is a SPRITE_GAP (4 pixels) between sprites
        - The spritesheet has SPRITESHEET_COLS columns and SPRITESHEET_ROWS rows

        According to the requirements:
        - The first four tiles in a row are grass types
        - The next two are dirt
        - The next five are gray tiles
        """
        # Extract all tiles from the spritesheet with generic names
        for row in range(SPRITESHEET_ROWS):
            for col in range(SPRITESHEET_COLS):
                # Calculate position with gaps
                x = col * (SPRITE_SIZE + SPRITE_GAP)
                y = row * (SPRITE_SIZE + SPRITE_GAP)

                # Extract sprite from spritesheet
                sprite_rect = pygame.Rect(x, y, SPRITE_SIZE, SPRITE_SIZE)

                # Make sure the rect is within the surface bounds
                if (x + SPRITE_SIZE <= surface.get_width() and 
                    y + SPRITE_SIZE <= surface.get_height()):
                    try:
                        sprite_surface = surface.subsurface(sprite_rect).copy()

                        # Scale to TILE_SIZE if needed
                        if SPRITE_SIZE != TILE_SIZE:
                            sprite_surface = pygame.transform.scale(sprite_surface, (TILE_SIZE, TILE_SIZE))

                        # Determine the tile type based on its position in the row
                        if col < 4:
                            # First four tiles in a row are grass types
                            tile_type = "grass"
                        elif col < 6:
                            # Next two tiles are dirt
                            tile_type = "dirt"
                        elif col < 11:
                            # Next five tiles are gray tiles
                            tile_type = "gray"
                        else:
                            # Other tiles get a generic type
                            tile_type = "misc"

                        # Store sprite in texture atlas
                        tile_name = f"{tile_type}_{row}_{col}"
                        self._texture_atlas.add_texture("tile", tile_name, sprite_surface)

                        # For backward compatibility
                        legacy_name = f"tile_{tile_type}_{row}_{col}"
                        self._sprites[legacy_name] = sprite_surface

                        # Also store with a more specific name for backward compatibility
                        if col == 0 and row == 0:
                            self._sprites['tile_grass'] = sprite_surface
                            self._texture_atlas.add_texture("tile", "grass", sprite_surface)
                        elif col == 4 and row == 0:
                            self._sprites['tile_dirt'] = sprite_surface
                            self._texture_atlas.add_texture("tile", "dirt", sprite_surface)
                        elif col == 6 and row == 0:
                            self._sprites['tile_wall_brick'] = sprite_surface
                            self._texture_atlas.add_texture("tile", "wall_brick", sprite_surface)
                        elif col == 20 and row == 6:
                            self._sprites['tile_tree'] = sprite_surface
                            self._texture_atlas.add_texture("tile", "tree", sprite_surface)
                        elif col == 15 and row == 2:
                            self._sprites['tile_building_floor'] = sprite_surface
                            self._texture_atlas.add_texture("tile", "building_wall", sprite_surface)
                    except ValueError as e:
                        print(f"Error extracting sprite at ({x}, {y}): {e}")

    def _load_individual_sprites(self) -> None:
        """Load individual sprite files into the texture atlas."""
        # Define sprite categories to load
        sprite_categories = ['weapon', 'survivor', 'zombie', 'pickups', 'sprites']

        for category in sprite_categories:
            folder_path = os.path.join(self.sprites_path, category)
            if os.path.exists(folder_path):
                print(f"Loading sprites from {folder_path}")
                for filename in os.listdir(folder_path):
                    if filename.endswith(('.png', '.jpg', '.jpeg')):
                        filepath = os.path.join(folder_path, filename)
                        # Get sprite name without extension
                        sprite_name = os.path.splitext(filename)[0]
                        try:
                            surface = pygame.image.load(filepath).convert_alpha()
                            # Add to texture atlas
                            self._texture_atlas.add_texture(category, sprite_name, surface)
                            # For backward compatibility
                            legacy_name = f"{category}_{sprite_name}"
                            self._sprites[legacy_name] = surface
                        except pygame.error as e:
                            print(f"Warning: Could not load {filepath}: {e}")

    def _copy_textures_to_sprites(self) -> None:
        """Copy all textures from the texture atlas to the _sprites dictionary for backward compatibility."""
        for category in self._texture_atlas.get_categories():
            for name in self._texture_atlas.get_textures_in_category(category):
                texture = self._texture_atlas.get_texture(category, name)
                # Use both category_name format and just name for common sprites
                self._sprites[f"{category}_{name}"] = texture

    def _optimize_surfaces(self) -> None:
        """Optimize all loaded surfaces for better performance."""
        for name, surface in self._sprites.items():
            if surface.get_flags() & pygame.SRCALPHA:
                optimized = surface.convert_alpha()
            else:
                optimized = surface.convert()
            self._sprites[name] = optimized

    def _create_fallback_sprites(self) -> None:
        """Create simple colored rectangle fallback sprites when assets are missing.
        All missing textures are rendered in pink as specified in the requirements.
        """
        # Define fallback sprites with categories and names
        fallback_sprites = {
            ('player', 'idle'): (32, 32),
            ('survivor', 'survivor1_stand'): (32, 32),
            ('survivor', 'survivor1_gun'): (32, 32),
            ('survivor', 'survivor1_hold'): (32, 32),
            ('survivor', 'survivor1_machine'): (32, 32),
            ('survivor', 'survivor1_reload'): (32, 32),
            ('survivor', 'survivor1_silencer'): (32, 32),
            ('zombie', 'basic_1'): (24, 24),
            ('zombie', 'runner_1'): (20, 20),
            ('zombie', 'tank_1'): (40, 40),
            ('zombie', 'zoimbie1_stand'): (32, 32),
            ('zombie', 'zoimbie1_hold'): (32, 32),
            ('tile', 'grass'): (TILE_SIZE, TILE_SIZE),
            ('tile', 'tree'): (TILE_SIZE, TILE_SIZE),
            ('tile', 'wall_brick'): (TILE_SIZE, TILE_SIZE),
            ('tile', 'building_wall'): (TILE_SIZE, TILE_SIZE),
            ('weapon', 'pistol'): (ITEM_SIZE, ITEM_SIZE),
            ('weapon', 'shotgun'): (ITEM_SIZE, ITEM_SIZE),
            ('weapon', 'assault_rifle'): (ITEM_SIZE, ITEM_SIZE),
            ('weapon', 'sniper_rifle'): (ITEM_SIZE, ITEM_SIZE),
            ('weapon', 'explosives'): (ITEM_SIZE, ITEM_SIZE),  # For bazooka
            ('pickups', 'health'): (64, 64),
            ('pickups', 'ammo'): (64, 64),
            ('pickups', 'more_speed'): (64, 64),
            ('pickups', 'more_damage'): (64, 64),
            ('pickups', 'regeneration'): (64, 64),
            ('pickups', 'invincibility'): (64, 64)
        }

        # Create fallback sprites for items
        for (category, name), (width, height) in fallback_sprites.items():
            # Check if the sprite exists in the texture atlas
            if self._texture_atlas.get_texture(category, name) is None:
                # Create a pink fallback sprite
                surface = pygame.Surface((width, height), pygame.SRCALPHA)
                surface.fill(self._missing_texture_color)

                # Add to texture atlas
                self._texture_atlas.add_texture(category, name, surface)

                # For backward compatibility
                legacy_name = f"{category}_{name}"
                self._sprites[legacy_name] = surface.convert_alpha()

                print(f"Created fallback sprite for {category}/{name}")

    def get_sprite(self, name: str) -> Optional[pygame.Surface]:
        """Get a sprite by name.

        This method is maintained for backward compatibility.
        For new code, use get_texture() instead.
        """
        if not self._loaded:
            self.load_all_assets()

        return self._sprites.get(name)

    def get_texture(self, category: str, name: str) -> Optional[pygame.Surface]:
        """Get a texture from the texture atlas.

        Args:
            category (str): Category of the texture (e.g., 'weapon', 'player')
            name (str): Name of the texture

        Returns:
            Optional[pygame.Surface]: The texture surface, or None if not found
        """
        if not self._loaded:
            self.load_all_assets()

        return self._texture_atlas.get_texture(category, name)

    def get_scaled_sprite(self, name: str, scale: float) -> Optional[pygame.Surface]:
        """Get a scaled version of a sprite.

        This method is maintained for backward compatibility.
        For new code, use get_scaled_texture() instead.
        """
        sprite = self.get_sprite(name)
        if sprite is None:
            return None

        # Cache key for scaled sprite
        cache_key = f"{name}_scale_{scale}"
        if cache_key in self._sprites:
            return self._sprites[cache_key]

        # Scale the sprite
        original_size = sprite.get_size()
        new_size = (int(original_size[0] * scale), int(original_size[1] * scale))
        scaled_sprite = pygame.transform.scale(sprite, new_size)

        # Cache the scaled sprite
        self._sprites[cache_key] = scaled_sprite
        return scaled_sprite

    def get_scaled_texture(self, category: str, name: str, scale: float) -> Optional[pygame.Surface]:
        """Get a scaled version of a texture.

        Args:
            category (str): Category of the texture
            name (str): Name of the texture
            scale (float): Scale factor

        Returns:
            Optional[pygame.Surface]: The scaled texture, or None if not found
        """
        texture = self.get_texture(category, name)
        if texture is None:
            return None

        # Cache key for scaled texture
        cache_key = f"{category}_{name}_scale_{scale}"
        if cache_key in self._sprites:
            return self._sprites[cache_key]

        # Scale the texture
        original_size = texture.get_size()
        new_size = (int(original_size[0] * scale), int(original_size[1] * scale))
        scaled_texture = pygame.transform.scale(texture, new_size)

        # Cache the scaled texture
        self._sprites[cache_key] = scaled_texture
        return scaled_texture

    def get_sprite_list(self) -> List[str]:
        """Get list of all available sprite names.

        This method is maintained for backward compatibility.
        For new code, use get_texture_categories() and get_textures_in_category() instead.
        """
        if not self._loaded:
            self.load_all_assets()
        return list(self._sprites.keys())

    def get_texture_categories(self) -> List[str]:
        """Get all texture categories in the atlas.

        Returns:
            List[str]: List of all texture categories
        """
        if not self._loaded:
            self.load_all_assets()
        return self._texture_atlas.get_categories()

    def get_textures_in_category(self, category: str) -> List[str]:
        """Get all texture names in a category.

        Args:
            category (str): Category to get textures from

        Returns:
            List[str]: List of texture names in the category
        """
        if not self._loaded:
            self.load_all_assets()
        return self._texture_atlas.get_textures_in_category(category)

    def get_asset_info(self) -> Dict[str, Any]:
        """Get information about loaded assets."""
        if not self._loaded:
            self.load_all_assets()

        # Count textures in the atlas
        total_textures = sum(len(textures) for textures in self._texture_atlas.get_all_textures().values())

        # Get texture categories and counts
        texture_categories = {}
        for category in self._texture_atlas.get_categories():
            texture_categories[category] = len(self._texture_atlas.get_textures_in_category(category))

        return {
            'total_sprites': len(self._sprites),
            'total_spritesheets': len(self._spritesheets),
            'total_textures': total_textures,
            'texture_categories': texture_categories,
            'sprite_names': list(self._sprites.keys()),
            'spritesheet_names': list(self._spritesheets.keys()),
        }

    def debug_sprite_info(self) -> None:
        """Print debug information about loaded sprites and textures."""
        if not self._loaded:
            self.load_all_assets()

        print(f"Total sprites loaded: {len(self._sprites)}")
        print(f"Total spritesheets loaded: {len(self._spritesheets)}")

        # Count textures in the atlas
        total_textures = sum(len(textures) for textures in self._texture_atlas.get_all_textures().values())
        print(f"Total textures in atlas: {total_textures}")

        print("\nTexture Atlas Categories:")
        for category in self._texture_atlas.get_categories():
            textures = self._texture_atlas.get_textures_in_category(category)
            print(f"  {category}: {len(textures)} textures")
            # Print first 5 textures in each category
            for i, name in enumerate(textures[:5]):
                texture = self._texture_atlas.get_texture(category, name)
                print(f"    {name}: {texture.get_width()}x{texture.get_height()} pixels")
            if len(textures) > 5:
                print(f"    ... and {len(textures) - 5} more")

        print("\nSpritesheets:")
        for name, sheet in self._spritesheets.items():
            print(f"  {name}: {sheet.get_width()}x{sheet.get_height()} pixels")

        print("\nSprites (legacy format):")
        # Print first 20 sprites
        sprite_items = list(self._sprites.items())
        for name, sprite in sprite_items[:20]:
            print(f"  {name}: {sprite.get_width()}x{sprite.get_height()} pixels")
        if len(sprite_items) > 20:
            print(f"  ... and {len(sprite_items) - 20} more")

# Global asset manager instance
asset_manager = AssetManager()

def get_sprite(name: str) -> Optional[pygame.Surface]:
    """Convenience function to get a sprite (legacy format)."""
    return asset_manager.get_sprite(name)

def get_texture(category: str, name: str) -> Optional[pygame.Surface]:
    """Convenience function to get a texture from the texture atlas.

    Args:
        category (str): Category of the texture (e.g., 'weapon', 'player')
        name (str): Name of the texture

    Returns:
        Optional[pygame.Surface]: The texture surface, or None if not found
    """
    return asset_manager.get_texture(category, name)

def get_scaled_sprite(name: str, scale: float) -> Optional[pygame.Surface]:
    """Convenience function to get a scaled sprite (legacy format)."""
    return asset_manager.get_scaled_sprite(name, scale)

def get_scaled_texture(category: str, name: str, scale: float) -> Optional[pygame.Surface]:
    """Convenience function to get a scaled texture.

    Args:
        category (str): Category of the texture
        name (str): Name of the texture
        scale (float): Scale factor

    Returns:
        Optional[pygame.Surface]: The scaled texture, or None if not found
    """
    return asset_manager.get_scaled_texture(category, name, scale)

def get_texture_categories() -> List[str]:
    """Convenience function to get all texture categories."""
    return asset_manager.get_texture_categories()

def get_textures_in_category(category: str) -> List[str]:
    """Convenience function to get all texture names in a category."""
    return asset_manager.get_textures_in_category(category)

def load_all_assets() -> None:
    """Convenience function to load all assets."""
    asset_manager.load_all_assets()

def get_asset_info() -> Dict[str, Any]:
    """Convenience function to get asset information."""
    return asset_manager.get_asset_info()

def debug_sprite_info() -> None:
    """Convenience function to print debug information about loaded sprites and textures."""
    asset_manager.debug_sprite_info()
