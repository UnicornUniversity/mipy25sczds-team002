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
ZOMBIE_COLLISION_RADIUS = 20  # Radius for zombie-zombie collision
ZOMBIE_OBSTACLE_COLLISION_RADIUS = 16  # Radius for zombie-obstacle collision

# Speeds
PLAYER_SPEED = 200  # pixels per second
ENEMY_SPEED = 100
TOUGH_ZOMBIE_SPEED = 70  # Slower than regular zombies
OBJECT_SPEED_MULTIPLIER = 0.6  # Speed multiplier when moving over objects

# Health and Damage
PLAYER_MAX_HEALTH = 100
ZOMBIE_HEALTH = 30
ZOMBIE_DAMAGE = 5
TOUGH_ZOMBIE_HEALTH = 60  # Tougher than regular zombies
TOUGH_ZOMBIE_DAMAGE = 10  # More damage than regular zombies
ZOMBIE_ATTACK_COOLDOWN = 1.0  # Seconds between zombie attacks
ZOMBIE_ATTACK_RANGE = 30  # Distance at which zombie can attack player
ZOMBIE_ATTACK_DURATION = 0.3  # Duration of attack animation
ZOMBIE_ATTACK_KNOCKBACK = 50  # How far to knock back player when hit

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

# Items
ITEM_SIZE = 16
HEALTH_PACK_COLOR = RED
WEAPON_COLOR = BLUE
POWERUP_COLOR = GREEN
HEALTH_PACK_HEAL_AMOUNT = 25
PICKUP_NOTIFICATION_DURATION = 3.0  # seconds

# Weapons
BULLET_SIZE = 6
BULLET_SPEED = 500  # pixels per second
BULLET_COLOR = BLACK

# Pistol - Balanced damage/fire rate
PISTOL_DAMAGE = 10
PISTOL_SPREAD = 0.2  # radians (about 11 degrees)
PISTOL_MAGAZINE_SIZE = 12
PISTOL_RELOAD_TIME = 1.5  # seconds
PISTOL_COOLDOWN = 0.3  # seconds between shots
PISTOL_BULLET_COLOR = BLACK

# Shotgun - High damage at close range, slow reload
SHOTGUN_DAMAGE = 5  # per pellet
SHOTGUN_PELLETS = 8  # number of pellets per shot
SHOTGUN_SPREAD = 0.4  # radians (wider spread)
SHOTGUN_MAGAZINE_SIZE = 6
SHOTGUN_RELOAD_TIME = 2.5  # seconds
SHOTGUN_COOLDOWN = 0.8  # seconds between shots
SHOTGUN_BULLET_COLOR = RED

# Assault Rifle - Rapid fire, medium damage
ASSAULT_RIFLE_DAMAGE = 8
ASSAULT_RIFLE_SPREAD = 0.25  # radians
ASSAULT_RIFLE_MAGAZINE_SIZE = 30
ASSAULT_RIFLE_RELOAD_TIME = 2.0  # seconds
ASSAULT_RIFLE_COOLDOWN = 0.1  # seconds between shots (rapid fire)
ASSAULT_RIFLE_BULLET_COLOR = BLUE

# Sniper Rifle - High damage, slow fire rate, high accuracy
SNIPER_RIFLE_DAMAGE = 50
SNIPER_RIFLE_SPREAD = 0.05  # radians (very accurate)
SNIPER_RIFLE_MAGAZINE_SIZE = 5
SNIPER_RIFLE_RELOAD_TIME = 3.0  # seconds
SNIPER_RIFLE_COOLDOWN = 1.5  # seconds between shots
SNIPER_RIFLE_BULLET_COLOR = GREEN
SNIPER_RIFLE_BULLET_SPEED = 800  # faster bullet

# Bazooka - Explosive damage, very slow fire rate
BAZOOKA_DAMAGE = 100
BAZOOKA_SPREAD = 0.1  # radians
BAZOOKA_MAGAZINE_SIZE = 1
BAZOOKA_RELOAD_TIME = 4.0  # seconds
BAZOOKA_COOLDOWN = 2.0  # seconds between shots
BAZOOKA_BULLET_COLOR = BROWN
BAZOOKA_EXPLOSION_RADIUS = 100  # pixels
BAZOOKA_BULLET_SPEED = 300  # slower bullet

# General weapon settings
WEAPON_COOLDOWN = 0.3  # default cooldown for weapons
