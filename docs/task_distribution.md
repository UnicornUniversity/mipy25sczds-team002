# Deadlock - Task Distribution

This document outlines the distribution of tasks among the 3 team members for the development of Deadlock. Tasks are organized by system/feature and assigned to specific team members based on their strengths and to ensure balanced workload. The timeline has been adjusted to accommodate a 2-day development period.

> **Note:** This document has been updated to reflect a more realistic scope for a 3-person team with a 2-day development timeline. Tasks marked with "(Optional)" are lower priority and should only be implemented if time permits.

## Team Member 1: Core Game Systems & Player Mechanics

### Responsibilities
- Game state management and main loop
- Player movement and controls
- Player health and damage system
- Collision detection system
- Camera system
- Game settings and configuration
- Weapon system and mechanics (redistributed from Team Member 4)
- User interface (HUD, menus) (redistributed from Team Member 4)

### Specific Tasks
1. Implement player character with movement controls (WASD/arrows)
2. Create health system with damage and healing mechanics
3. Implement dodge roll mechanic with cooldown (Optional)
4. Set up collision detection for player and environment
5. Create camera system that follows player
6. Implement game over condition and state transition
7. Extend settings system for game configuration
8. Implement basic weapon system with pistol
9. Create ammo and reload mechanics
10. Design and implement HUD (health bar, ammo counter, score)
11. Create menu screens (main menu, pause, game over)

## Team Member 2: Map Generation & Environment

### Responsibilities
- Procedural map generation
- Environment objects and obstacles
- Building interiors and exteriors
- Item and pickup system (redistributed from Team Member 4)
- Score system (redistributed from Team Member 4)
- Art asset coordination

### Specific Tasks
1. Create procedural map generation algorithm
2. Implement various environment objects (trees, cars, barricades)
3. Design and implement buildings with interiors (Optional)
4. Design map boundaries
5. Create object placement algorithm for balanced gameplay
6. Implement item pickup system
7. Create health packs and ammo pickups
8. Implement score system and high score tracking
9. Coordinate art assets and ensure visual consistency

## Team Member 3: Enemy System & AI

### Responsibilities
- Zombie types and behaviors
- Pathfinding system
- Enemy spawning system
- Difficulty scaling
- Sound effects and music (redistributed from Team Member 4)
- Visual effects (redistributed from Team Member 4)

### Specific Tasks
1. Implement basic zombie enemy with AI
2. Create additional zombie types (runner, tank) (Optional)
3. Implement A* pathfinding for zombies to track player
4. Create spawn system with increasing difficulty over time
5. Implement zombie attack mechanics and animations
6. Add sound effects for weapons, zombies, and player
7. Implement basic music system
8. Create simple visual effects for impacts and damage


## Shared Responsibilities

### Art Assets
- Each team member will contribute to creating or finding appropriate pixel art assets for their assigned systems
- Team Member 2 will coordinate the overall art style and ensure consistency

### Testing
- All team members will participate in testing
- Each member will be responsible for testing their own systems
- Weekly group testing sessions to identify and fix integration issues

### Documentation
- Each team member will document their code and systems
- Team Member 1 will coordinate overall documentation

## Development Timeline

### Day 1: Core Systems and Basic Gameplay
- Set up project structure and basic game loop
- Implement player movement and basic controls
- Create simple map generation
- Add basic zombie enemy with pathfinding
- Implement collision detection
- Create basic weapon system (pistol)
- Implement health system
- Design and implement basic UI elements (health bar, score)

### Day 2: Refinement and Integration
- Add item pickups (health, ammo)
- Implement difficulty scaling
- Create menu screens (main menu, game over)
- Add sound effects and basic music
- Implement score system
- Add simple visual effects
- Testing and bug fixing
- Final adjustments and integration
