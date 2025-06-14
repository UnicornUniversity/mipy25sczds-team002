"""
Building templates for the map generator.

This file contains templates for buildings of different sizes.
Each template is a 2D list where:
- 0 = no change (keep existing tile)
- 1 = wall
- 2 = wood (floor)

Templates should have doors (openings in the walls) to allow entry.
"""

# Small building templates (7x7)
SMALL_BUILDINGS = [
    # Small house with door at the bottom
    [
        [1, 1, 1, 1, 1, 1, 1],
        [1, 2, 2, 2, 2, 2, 1],
        [1, 2, 2, 2, 2, 2, 1],
        [1, 2, 2, 2, 2, 2, 1],
        [1, 2, 2, 2, 2, 2, 1],
        [1, 2, 2, 2, 2, 2, 1],
        [1, 1, 1, 2, 2, 1, 1]  # Door at the bottom
    ],
    
    # Small house with door on the right
    [
        [1, 1, 1, 1, 1, 1, 1],
        [1, 2, 2, 2, 2, 2, 1],
        [1, 2, 2, 2, 2, 2, 1],
        [1, 2, 2, 2, 2, 2, 2],  # Door on the right
        [1, 2, 2, 2, 2, 2, 2],  # Door on the right
        [1, 2, 2, 2, 2, 2, 1],
        [1, 1, 1, 1, 1, 1, 1]
    ],
    
    # Small house with door on the left
    [
        [1, 1, 1, 1, 1, 1, 1, 2, 2, 1],
        [1, 2, 2, 2, 2, 2, 1, 2, 2, 1],
        [1, 2, 2, 2, 2, 2, 1, 2, 2, 1],
        [2, 2, 2, 2, 2, 2, 1, 2, 2, 1],  # Door on the left
        [2, 2, 2, 2, 2, 2, 2, 2, 2, 1],  # Door on the left
        [1, 2, 2, 2, 2, 2, 1, 2, 2, 1],
        [1, 1, 1, 1, 1, 1, 1, 2, 2, 1]
    ]
]

# Medium building templates (9x9)
MEDIUM_BUILDINGS = [
    # Original building from map_generator.py
    [
        [1, 1, 1, 1, 1, 1, 1, 1, 1],
        [1, 2, 2, 2, 1, 2, 2, 2, 1],
        [1, 2, 2, 2, 2, 2, 2, 2, 1],
        [1, 2, 2, 2, 2, 2, 2, 2, 1],
        [1, 1, 2, 2, 2, 2, 2, 1, 1],
        [1, 2, 2, 2, 2, 2, 2, 2, 1],
        [1, 2, 2, 2, 2, 2, 2, 2, 1],
        [1, 2, 2, 2, 2, 2, 2, 2, 1],
        [1, 1, 1, 1, 0, 0, 1, 1, 1]  # Door at the bottom
    ],
    
    # Medium house with two rooms and door on the right
    [
        [1, 1, 1, 1, 1, 1, 1, 1, 1],
        [1, 2, 2, 2, 1, 2, 2, 2, 1],
        [1, 2, 2, 2, 1, 2, 2, 2, 1],
        [1, 2, 2, 2, 2, 2, 2, 2, 2],  # Internal door and external door
        [1, 2, 2, 2, 2, 2, 2, 2, 2],  # External door continues
        [1, 1, 1, 1, 1, 2, 2, 2, 1],
        [0, 0, 0, 0, 1, 2, 2, 2, 1],
        [0, 0, 0, 0, 1, 2, 2, 2, 1],
        [0, 0, 0, 0, 1, 1, 1, 1, 1]
    ],
    
    # Medium house with central courtyard
    [
        [1, 1, 1, 1, 1, 1, 1, 1, 1],
        [1, 2, 2, 2, 2, 2, 2, 2, 1],
        [1, 2, 2, 1, 1, 1, 2, 2, 1],
        [1, 2, 2, 1, 0, 1, 2, 2, 1],  # Courtyard (0 = grass)
        [1, 2, 2, 1, 0, 1, 1, 1, 1],  # Courtyard (0 = grass)
        [1, 2, 2, 1, 0, 1, 2, 2, 1],  # Courtyard (0 = grass)
        [1, 2, 2, 1, 1, 1, 2, 2, 1],  # Door to courtyard
        [1, 2, 2, 2, 2, 2, 2, 2, 1],
        [1, 1, 1, 2, 2, 1, 1, 1, 1]   # Door at the bottom
    ]
]

# Large building templates (12x12)
LARGE_BUILDINGS = [
    # Large house with multiple rooms
    [
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        [1, 2, 2, 2, 1, 2, 2, 2, 1, 2, 2, 1],
        [1, 2, 2, 2, 1, 2, 2, 2, 1, 2, 2, 1],
        [1, 2, 2, 2, 1, 2, 2, 2, 1, 2, 2, 1],
        [1, 2, 2, 2, 1, 1, 2, 1, 1, 2, 2, 1],  # Internal doors
        [2, 2, 2, 2, 2, 2, 2, 2, 1, 2, 2, 1],
        [2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 1],
        [1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 1],  # Internal door
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 2, 1],
        [1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 1],
        [1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 1],
        [1, 1, 1, 1, 1, 1, 1, 1, 2, 2, 1, 1]   # Door at the bottom right
    ],
    
    # Large warehouse with wide entrance
    [
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        [1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 1],
        [1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 1],
        [1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 1],
        [1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 1],
        [1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 1],
        [1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 1],
        [1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 1],
        [1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 1],
        [1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 1],
        [1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 1],
        [1, 1, 1, 1, 2, 2, 2, 2, 1, 1, 1, 1]   # Wide door at the bottom
    ]
]

# All building templates combined for easy access
ALL_BUILDINGS = SMALL_BUILDINGS + MEDIUM_BUILDINGS + LARGE_BUILDINGS