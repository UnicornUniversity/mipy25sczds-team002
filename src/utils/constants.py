WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
FPS = 60

# Debug
DEBUG_FONT_SIZE = 20
DEBUG_TEXT_COLOR = (255, 0, 0)  # Yellow

# Colors (RGB)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
GRAY = (100, 100, 100)
BROWN = (139, 69, 19)
DARK_GREEN = (0, 100, 0)
LIGHT_GREEN = (144, 238, 144)
DARK_BROWN = (101, 67, 33)

# Sizes
PLAYER_SIZE = 32
ENEMY_SIZE = 24

# Speeds
PLAYER_SPEED = 200  # pixels per second
ENEMY_SPEED = 100
OBJECT_SPEED_MULTIPLIER = 0.6  # Speed multiplier when moving over objects

# Background
DOT_SIZE = 2
DOT_SPACING = 50

# Camera
CAMERA_LERP = 0.1  # Camera smoothing factor (0-1)

# Map
TILE_SIZE = 32
MAP_WIDTH = 80  # tiles
MAP_HEIGHT = 80  # tiles
EDGE_THICKNESS = 5  # thickness of forest edge in tiles
MIN_BUILDINGS = 4  # Minimum number of buildings to generate
MAX_BUILDINGS = 7  # Maximum number of buildings to generate
RANDOM_OBJECT_DENSITY = 0.03  # Probability of placing a random object (was 0.05)

# Tile types
TILE_GRASS = 0
TILE_OBJECT = 1  # trees, rocks, etc.
TILE_WALL = 2
TILE_WOOD = 3

# Tile colors
TILE_COLORS = {
    TILE_GRASS: LIGHT_GREEN,
    TILE_OBJECT: DARK_GREEN,
    TILE_WALL: GRAY,
    TILE_WOOD: BROWN
}

# Asset Management Constants
# ===========================

# Visual Consistency Settings
PIXEL_ART_SCALE = 1.0  # Scale factor for pixel art
SPRITE_ANTI_ALIAS = False  # Keep pixel art crisp

# Asset Categories (for organization)
ASSET_CATEGORIES = {
    'characters': ['player', 'zombie'],
    'tiles': ['grass', 'dirt', 'stone', 'wall', 'tree', 'building'],
    'weapons': ['pistol', 'rifle', 'shotgun'],
    'items': ['health', 'ammo', 'key'],
    'effects': ['muzzle_flash', 'blood', 'explosion'],
    'ui': ['button', 'bar', 'icon']
}

# Color Palette (for visual consistency)
COLOR_PALETTE = {
    # Player colors
    'player_primary': (60, 120, 60),     # Dark green
    'player_secondary': (100, 160, 100), # Light green
    
    # Enemy colors
    'zombie_basic': (150, 50, 50),       # Dark red
    'zombie_runner': (200, 100, 50),     # Orange
    'zombie_tank': (100, 30, 30),        # Very dark red
    
    # Environment colors
    'tile_grass': (50, 120, 50),         # Grass green
    'tile_dirt': (120, 80, 40),          # Brown dirt
    'tile_wall_brick': (120, 80, 60),    # Brick brown
    'tile_wall_concrete': (100, 100, 100), # Gray concrete
    'tile_tree': (34, 139, 34),          # Forest green
    'tile_building_wall': (105, 105, 105), # Gray building
    
    # Item colors
    'item_health': (100, 200, 100),      # Bright green
    'item_ammo': (200, 200, 50),         # Yellow
    'item_weapon': (150, 150, 150),      # Gray metal
    
    # UI colors
    'ui_primary': (40, 40, 60),          # Dark blue-gray
    'ui_secondary': (80, 80, 120),       # Light blue-gray
    'ui_accent': (255, 200, 50),         # Golden yellow
    'ui_health': (200, 50, 50),          # Red for health bars
    'ui_ammo': (200, 200, 50),           # Yellow for ammo
}

# Performance Optimization Settings
SPRITE_CACHE_SIZE = 256  # Maximum number of cached sprite variations
ENABLE_SPRITE_OPTIMIZATION = True  # Enable surface optimization

# Asset Quality Settings
TEXTURE_FILTER = 'nearest'  # For pixel art (nearest/linear)
COMPRESSION_QUALITY = 95    # PNG compression quality (0-100)
