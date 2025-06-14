import random
import pygame
from utils.constants import (
    TILE_SIZE, MAP_WIDTH, MAP_HEIGHT, EDGE_THICKNESS,
    TILE_GRASS, TILE_OBJECT, TILE_WALL, TILE_WOOD,
    TILE_COLORS, MIN_BUILDINGS, MAX_BUILDINGS, RANDOM_OBJECT_DENSITY
)
from utils.sprite_loader import get_sprite
from game.building_templates import SMALL_BUILDINGS, MEDIUM_BUILDINGS, LARGE_BUILDINGS, ALL_BUILDINGS

class MapGenerator:
    """Map generator for the game"""

    def __init__(self):
        """Initialize the map generator"""
        # Create an empty map matrix
        self.map_data = [[TILE_GRASS for _ in range(MAP_WIDTH)] for _ in range(MAP_HEIGHT)]

        # Generate the map
        self._generate_map()

        # Create a surface for the map
        self.map_surface = self._create_map_surface()

    def _generate_map(self):
        """Generate the map with grass, objects, walls, and wood"""
        # Step 1: Fill the entire map with grass (already done in initialization)

        # Step 2: Add dense forest (objects) around the edges
        self._add_forest_edge()

        # Step 3: Add buildings according to templates
        self._add_buildings()

        # Step 4: Add random objects throughout the map
        self._add_random_objects()

    def _add_forest_edge(self):
        """Add a dense forest around the edges of the map"""
        # Add objects along the top and bottom edges
        for x in range(MAP_WIDTH):
            for y in range(EDGE_THICKNESS):
                # Top edge
                if random.random() < 0.4:  # 40% chance for an object
                    self.map_data[y][x] = TILE_OBJECT

                # Bottom edge
                if random.random() < 0.4:
                    self.map_data[MAP_HEIGHT - 1 - y][x] = TILE_OBJECT

        # Add objects along the left and right edges
        for y in range(MAP_HEIGHT):
            for x in range(EDGE_THICKNESS):
                # Left edge
                if random.random() < 0.4:
                    self.map_data[y][x] = TILE_OBJECT

                # Right edge
                if random.random() < 0.4:
                    self.map_data[y][MAP_WIDTH - 1 - x] = TILE_OBJECT

    def _add_buildings(self):
        """Add buildings to the map using templates from building_templates.py"""
        # Determine how many buildings to add
        num_buildings = random.randint(MIN_BUILDINGS, MAX_BUILDINGS)

        # Keep track of building positions to prevent overlapping
        building_positions = []

        # Try to place each building
        for _ in range(num_buildings):
            # Randomly select a building template category with weighted probability
            # More small buildings, fewer large ones
            template_category = random.choices(
                [SMALL_BUILDINGS, MEDIUM_BUILDINGS, LARGE_BUILDINGS],
                weights=[0.5, 0.3, 0.2],
                k=1
            )[0]

            # Randomly select a template from the category
            building_template = random.choice(template_category)
            template_size = len(building_template)

            # Try to find a valid position for the building (not overlapping with existing buildings)
            max_attempts = 50  # Limit the number of attempts to avoid infinite loop
            overlaps = True

            for attempt in range(max_attempts):
                # Choose a random position for the building (away from edges)
                x = random.randint(EDGE_THICKNESS + 2, MAP_WIDTH - EDGE_THICKNESS - template_size - 2)
                y = random.randint(EDGE_THICKNESS + 2, MAP_HEIGHT - EDGE_THICKNESS - template_size - 2)

                # Check if this position overlaps with any existing building
                overlaps = False
                for bx, by, bs in building_positions:
                    # Check if buildings would overlap (with a small buffer)
                    if (abs(x - bx) < (template_size + bs) // 2 and 
                        abs(y - by) < (template_size + bs) // 2):
                        overlaps = True
                        break

                # If no overlap, we can place the building here
                if not overlaps:
                    building_positions.append((x, y, template_size))
                    break

            # If we couldn't find a valid position after max_attempts, skip this building
            if overlaps:
                continue

            # Apply the template to the map
            for ty in range(template_size):
                for tx in range(template_size):
                    template_value = building_template[ty][tx]
                    # Only change if template specifies a tile (not 0)
                    if template_value == 1:
                        self.map_data[y + ty][x + tx] = TILE_WALL
                    elif template_value == 2:
                        self.map_data[y + ty][x + tx] = TILE_WOOD

    def _add_random_objects(self):
        """Add random objects throughout the map"""
        # Add objects randomly throughout the map (excluding edges and buildings)
        for y in range(EDGE_THICKNESS, MAP_HEIGHT - EDGE_THICKNESS):
            for x in range(EDGE_THICKNESS, MAP_WIDTH - EDGE_THICKNESS):
                # Skip if the tile is already a wall or wood (part of a building)
                if self.map_data[y][x] == TILE_WALL or self.map_data[y][x] == TILE_WOOD:
                    continue

                # Use RANDOM_OBJECT_DENSITY to determine chance to place an object
                if random.random() < RANDOM_OBJECT_DENSITY:
                    self.map_data[y][x] = TILE_OBJECT

    def _get_sprite_for_tile(self, tile_type):
        """Get the appropriate sprite for a tile type with fallback

        According to the requirements:
        - Grass tiles should be randomly selected from the first four in the row
        - Objects should use dirt textures
        - Walls should use gray tiles
        - Wood should use wood textures
        """
        # Use a random grass texture for grass tiles
        if tile_type == TILE_GRASS:
            # Randomly select one of the first four tiles in the first row (grass types)
            col = random.randint(0, 3)
            sprite_name = f"tile_grass_0_{col}"
        # Use dirt textures for objects
        elif tile_type == TILE_OBJECT:
            # Randomly select one of the two dirt tiles
            col = random.randint(4, 5)
            sprite_name = f"tile_dirt_0_{col}"
        # Use gray tiles for walls
        elif tile_type == TILE_WALL:
            # Randomly select one of the five gray tiles
            col = random.randint(6, 10)
            sprite_name = f"tile_gray_0_{col}"
        # Use wood textures for wood
        elif tile_type == TILE_WOOD:
            # Use a specific wood texture
            sprite_name = "tile_building_wall"
        else:
            # Default to grass
            sprite_name = "tile_grass_0_0"

        sprite = get_sprite(sprite_name)

        # If sprite not found, try fallback to old names
        if sprite is None:
            fallback_mapping = {
                TILE_GRASS: 'tile_grass',
                TILE_OBJECT: 'tile_tree',
                TILE_WALL: 'tile_wall_brick',
                TILE_WOOD: 'tile_building_wall'
            }
            fallback_name = fallback_mapping.get(tile_type, 'tile_grass')
            sprite = get_sprite(fallback_name)

        # If still not found, create fallback colored rectangle
        if sprite is None:
            sprite = pygame.Surface((TILE_SIZE, TILE_SIZE))
            sprite.fill(TILE_COLORS[tile_type])

        return sprite

    def _create_map_surface(self):
        """Create a surface with the map rendered using sprites"""
        # Create a surface large enough for the entire map
        surface_width = MAP_WIDTH * TILE_SIZE
        surface_height = MAP_HEIGHT * TILE_SIZE
        surface = pygame.Surface((surface_width, surface_height))

        # Draw each tile on the surface using sprites
        for y in range(MAP_HEIGHT):
            for x in range(MAP_WIDTH):
                tile_type = self.map_data[y][x]

                # Get sprite for this tile type
                sprite = self._get_sprite_for_tile(tile_type)

                # Calculate position
                pos_x = x * TILE_SIZE
                pos_y = y * TILE_SIZE

                # Draw the sprite
                surface.blit(sprite, (pos_x, pos_y))

        return surface

    def get_tile_at(self, x, y):
        """Get the tile type at the specified world coordinates"""
        # Convert world coordinates to tile coordinates
        tile_x = int(x // TILE_SIZE)
        tile_y = int(y // TILE_SIZE)

        # Check if the coordinates are within the map bounds
        if 0 <= tile_x < MAP_WIDTH and 0 <= tile_y < MAP_HEIGHT:
            return self.map_data[tile_y][tile_x]

        # Return object (forest) for out-of-bounds coordinates
        return TILE_OBJECT

    def is_walkable(self, x, y):
        """Check if the specified world coordinates are walkable"""
        tile_type = self.get_tile_at(x, y)

        # Grass, objects, and wood (floor inside buildings) are walkable
        return tile_type == TILE_GRASS or tile_type == TILE_OBJECT or tile_type == TILE_WOOD

    def render(self, screen, camera_offset):
        """Render the map to the screen with the specified camera offset"""
        # Calculate the visible portion of the map based on camera offset
        view_rect = pygame.Rect(
            camera_offset[0], 
            camera_offset[1], 
            screen.get_width(), 
            screen.get_height()
        )

        # Blit the visible portion of the map to the screen
        # The destination position is (0, 0) because we're blitting the already-offset portion
        screen.blit(self.map_surface, (0, 0), view_rect)
