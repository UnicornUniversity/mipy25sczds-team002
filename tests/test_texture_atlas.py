"""
Test script for the texture atlas implementation.
This script verifies that the texture atlas is working correctly and that items are using sprites instead of circles.
"""

import pygame
import sys
import os

# Add the src directory to the path so we can import modules from there
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from utils.sprite_loader import load_all_assets, get_texture, get_texture_categories, get_textures_in_category, debug_sprite_info
from entities.items import Item, HealthPack, Weapon, Powerup

def test_texture_atlas():
    """Test the texture atlas implementation."""
    # Initialize pygame
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Texture Atlas Test")
    
    # Load all assets
    load_all_assets()
    
    # Print debug information about loaded sprites and textures
    debug_sprite_info()
    
    # Print all texture categories
    print("\nTexture Categories:")
    categories = get_texture_categories()
    for category in categories:
        print(f"  {category}")
        
    # Print all textures in the 'weapon' category
    print("\nWeapon Textures:")
    weapon_textures = get_textures_in_category('weapon')
    for texture in weapon_textures:
        print(f"  {texture}")
        
    # Create some items to test
    items = [
        HealthPack(100, 100),
        Weapon(200, 100, "pistol"),
        Weapon(300, 100, "shotgun"),
        Weapon(400, 100, "assault_rifle"),
        Weapon(500, 100, "sniper_rifle"),
        Weapon(600, 100, "bazooka"),
        Powerup(100, 200)
    ]
    
    # Main loop
    clock = pygame.time.Clock()
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                
        # Clear the screen
        screen.fill((0, 0, 0))
        
        # Render the items
        for item in items:
            item.render(screen)
            
        # Update the display
        pygame.display.flip()
        clock.tick(60)
        
    pygame.quit()
    
if __name__ == "__main__":
    test_texture_atlas()