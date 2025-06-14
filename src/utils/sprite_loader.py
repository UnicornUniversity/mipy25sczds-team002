"""
Sprite Loader - Centralized Art Asset Management System
=======================================================

This module provides a comprehensive system for loading, optimizing, and managing
all art assets in the game. Ensures visual consistency and performance optimization.
"""

import pygame
import os
from typing import Dict, Tuple, Optional, List, Any
from utils.constants import TILE_SIZE

class AssetManager:
    """
    Centralized manager for all game art assets.
    Handles loading, caching, and optimization of sprites and textures.
    """
    
    def __init__(self):
        self._sprites: Dict[str, pygame.Surface] = {}
        self._spritesheets: Dict[str, pygame.Surface] = {}
        self._loaded = False
        
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
        
        self._loaded = True
        print(f"Asset loading complete. Loaded {len(self._sprites)} sprites.")
        
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
        if sheet_name == 'spritesheet_characters.png':
            self._extract_character_sprites(surface)
        elif sheet_name == 'spritesheet_tiles.png':
            self._extract_tile_sprites(surface)
    
    def _extract_character_sprites(self, surface: pygame.Surface) -> None:
        """Extract character sprites from character spritesheet."""
        sprite_size = 32
        cols = surface.get_width() // sprite_size
        rows = surface.get_height() // sprite_size
        
        character_types = [
            'player_idle', 'player_walk_1', 'player_walk_2', 'player_walk_3',
            'zombie_basic_1', 'zombie_basic_2', 'zombie_runner_1', 'zombie_runner_2',
            'zombie_tank_1', 'zombie_tank_2'
        ]
        
        sprite_index = 0
        for row in range(rows):
            for col in range(cols):
                if sprite_index < len(character_types):
                    x = col * sprite_size
                    y = row * sprite_size
                    
                    sprite_rect = pygame.Rect(x, y, sprite_size, sprite_size)
                    sprite_surface = surface.subsurface(sprite_rect).copy()
                    
                    sprite_name = character_types[sprite_index]
                    self._sprites[sprite_name] = sprite_surface
                    sprite_index += 1
    
    def _extract_tile_sprites(self, surface: pygame.Surface) -> None:
        """Extract environment tiles from tile spritesheet."""
        tile_size = TILE_SIZE
        cols = surface.get_width() // tile_size
        rows = surface.get_height() // tile_size
        
        tile_types = [
            'tile_grass', 'tile_dirt', 'tile_stone', 'tile_concrete',
            'tile_wall_brick', 'tile_wall_wood', 'tile_wall_metal', 'tile_wall_concrete',
            'tile_tree', 'tile_rock', 'tile_bush', 'tile_barrel',
            'tile_building_wall', 'tile_building_door', 'tile_building_window', 'tile_building_roof'
        ]
        
        sprite_index = 0
        for row in range(rows):
            for col in range(cols):
                if sprite_index < len(tile_types):
                    x = col * tile_size
                    y = row * tile_size
                    
                    tile_rect = pygame.Rect(x, y, tile_size, tile_size)
                    tile_surface = surface.subsurface(tile_rect).copy()
                    
                    tile_name = tile_types[sprite_index]
                    self._sprites[tile_name] = tile_surface
                    sprite_index += 1
    
    def _load_individual_sprites(self) -> None:
        """Load individual sprite files."""
        sprite_folders = ['weapons', 'items', 'effects', 'ui']
        
        for folder in sprite_folders:
            folder_path = os.path.join(self.sprites_path, folder)
            if os.path.exists(folder_path):
                for filename in os.listdir(folder_path):
                    if filename.endswith(('.png', '.jpg', '.jpeg')):
                        filepath = os.path.join(folder_path, filename)
                        sprite_name = f"{folder}_{os.path.splitext(filename)[0]}"
                        try:
                            surface = pygame.image.load(filepath).convert_alpha()
                            self._sprites[sprite_name] = surface
                        except pygame.error as e:
                            print(f"Warning: Could not load {filepath}: {e}")
    
    def _optimize_surfaces(self) -> None:
        """Optimize all loaded surfaces for better performance."""
        for name, surface in self._sprites.items():
            if surface.get_flags() & pygame.SRCALPHA:
                optimized = surface.convert_alpha()
            else:
                optimized = surface.convert()
            self._sprites[name] = optimized
    
    def _create_fallback_sprites(self) -> None:
        """Create simple colored rectangle fallback sprites when assets are missing."""
        fallback_sprites = {
            'player_idle': (32, 32, (0, 255, 0)),      # Green player
            'zombie_basic_1': (24, 24, (255, 0, 0)),   # Red zombie
            'zombie_runner_1': (20, 20, (255, 100, 0)), # Orange runner
            'zombie_tank_1': (40, 40, (150, 0, 0)),    # Dark red tank
            'tile_grass': (TILE_SIZE, TILE_SIZE, (50, 150, 50)),   # Green grass
            'tile_tree': (TILE_SIZE, TILE_SIZE, (34, 139, 34)),    # Forest green
            'tile_wall_brick': (TILE_SIZE, TILE_SIZE, (139, 69, 19)), # Brown brick
            'tile_building_wall': (TILE_SIZE, TILE_SIZE, (105, 105, 105)), # Gray building
        }
        
        for name, (width, height, color) in fallback_sprites.items():
            if name not in self._sprites:
                surface = pygame.Surface((width, height))
                surface.fill(color)
                self._sprites[name] = surface.convert()
    
    def get_sprite(self, name: str) -> Optional[pygame.Surface]:
        """Get a sprite by name."""
        if not self._loaded:
            self.load_all_assets()
        
        return self._sprites.get(name)
    
    def get_scaled_sprite(self, name: str, scale: float) -> Optional[pygame.Surface]:
        """Get a scaled version of a sprite."""
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
    
    def get_sprite_list(self) -> List[str]:
        """Get list of all available sprite names."""
        if not self._loaded:
            self.load_all_assets()
        return list(self._sprites.keys())
    
    def get_asset_info(self) -> Dict[str, Any]:
        """Get information about loaded assets."""
        return {
            'total_sprites': len(self._sprites),
            'total_spritesheets': len(self._spritesheets),
            'sprite_names': list(self._sprites.keys()),
            'spritesheet_names': list(self._spritesheets.keys()),
        }

# Global asset manager instance
asset_manager = AssetManager()

def get_sprite(name: str) -> Optional[pygame.Surface]:
    """Convenience function to get a sprite."""
    return asset_manager.get_sprite(name)

def get_scaled_sprite(name: str, scale: float) -> Optional[pygame.Surface]:
    """Convenience function to get a scaled sprite."""
    return asset_manager.get_scaled_sprite(name, scale)

def load_all_assets() -> None:
    """Convenience function to load all assets."""
    asset_manager.load_all_assets()

def get_asset_info() -> Dict[str, Any]:
    """Convenience function to get asset information."""
    return asset_manager.get_asset_info()
