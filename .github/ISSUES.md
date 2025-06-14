# Deadlock - GitHub Issues

This document contains GitHub issues for the Deadlock project, organized by milestone.

## Milestone: Day 1 - Essential Systems

### Issue 1: Set up project structure and basic game loop
**Assignee:** Team Member 1
**Labels:** setup, core
**Description:**
Initialize the project structure according to the implementation plan. Set up the main game loop with proper timing and state management. Ensure the basic framework is in place for other team members to build upon.

### Issue 2: Implement player character with movement controls
**Assignee:** Team Member 1
**Labels:** feature, player
**Description:**
Create the Player class extending the Entity base class. Implement movement controls using WASD/arrow keys. Ensure smooth movement with proper delta time handling. Add basic collision detection to prevent the player from moving through obstacles.

### Issue 3: Create health system with damage and healing mechanics
**Assignee:** Team Member 1
**Labels:** feature, player, gameplay
**Description:**
Implement a health system for the player. Add methods for taking damage and healing. Create visual feedback when the player takes damage. Implement game over condition when health reaches zero.

### Issue 4: Set up collision detection system
**Assignee:** Team Member 1
**Labels:** feature, core
**Description:**
Implement a collision detection system that can handle entity-entity and entity-environment collisions. Ensure the system is efficient and can scale with multiple entities. Integrate with the player movement system.

### Issue 5: Create camera system that follows player
**Assignee:** Team Member 1
**Labels:** feature, ui
**Description:**
Implement a camera system that smoothly follows the player. Add camera lerping for smooth transitions. Ensure the camera properly handles screen boundaries and map edges.

### Issue 6: Create procedural map generation algorithm
**Assignee:** Team Member 2
**Labels:** feature, environment
**Description:**
Implement a simple procedural map generation system. Create a tile-based map with different terrain types. Add basic obstacle placement. Ensure the generated maps are playable and balanced.

### Issue 7: Implement various environment objects
**Assignee:** Team Member 2
**Labels:** feature, environment
**Description:**
Create different types of environment objects (trees, cars, barricades). Implement collision for these objects. Ensure objects are properly rendered with correct z-ordering.

### Issue 8: Design map boundaries
**Assignee:** Team Member 2
**Labels:** feature, environment
**Description:**
Implement boundaries for the game map to prevent players from leaving the playable area. Add visual indicators for the boundaries. Ensure proper collision detection with the boundaries.

### Issue 9: Implement basic zombie enemy with AI
**Assignee:** Team Member 3
**Labels:** feature, enemy
**Description:**
Create the basic Zombie class extending the Entity base class. Implement simple AI behavior to follow and attack the player. Add appropriate animations and visual feedback. Ensure zombies can navigate around basic obstacles.

### Issue 10: Implement A* pathfinding for zombies
**Assignee:** Team Member 3
**Labels:** feature, ai
**Description:**
Implement a pathfinding system using the A* algorithm for zombies to efficiently navigate to the player. Optimize the algorithm for performance with multiple zombies. Integrate with the zombie AI behavior.

### Issue 11: Create spawn system with increasing difficulty
**Assignee:** Team Member 3
**Labels:** feature, gameplay
**Description:**
Implement a zombie spawning system that creates new zombies over time. Add difficulty scaling to increase spawn rate as time progresses. Ensure zombies spawn at appropriate locations away from the player.

## Milestone: Day 2 - Gameplay and Polish

### Issue 12: Implement basic weapon system with pistol
**Assignee:** Team Member 1
**Labels:** feature, weapons
**Description:**
Create a Weapon base class and implement a pistol as the primary weapon. Add shooting mechanics with proper cooldown and accuracy. Implement bullet collision detection and damage calculation.

### Issue 13: Create ammo and reload mechanics
**Assignee:** Team Member 1
**Labels:** feature, weapons
**Description:**
Add ammunition system for weapons. Implement reload mechanics with appropriate timing. Create visual and audio feedback for reloading. Add ammo count display to the UI.

### Issue 14: Design and implement HUD elements
**Assignee:** Team Member 1
**Labels:** feature, ui
**Description:**
Create HUD elements including health bar, ammo counter, and score display. Ensure the HUD is responsive and scales appropriately. Add visual feedback for low health and ammo.

### Issue 15: Create menu screens
**Assignee:** Team Member 1
**Labels:** feature, ui
**Description:**
Implement main menu, pause menu, and game over screens. Add navigation between screens. Ensure proper state management when transitioning between screens.

### Issue 16: Implement item pickup system
**Assignee:** Team Member 2
**Labels:** feature, items
**Description:**
Create a system for item pickups in the game world. Implement collision detection for pickups. Add visual feedback when items are collected.

### Issue 17: Create health packs and ammo pickups
**Assignee:** Team Member 2
**Labels:** feature, items
**Description:**
Implement health pack and ammo pickup items. Add appropriate visual representations. Ensure items properly affect player health and ammo when collected.

### Issue 18: Implement score system and high score tracking
**Assignee:** Team Member 2
**Labels:** feature, gameplay
**Description:**
Create a scoring system based on survival time and zombie kills. Implement high score tracking and persistence. Add a high score display to the game over screen.

### Issue 19: Coordinate art assets and ensure visual consistency
**Assignee:** Team Member 2
**Labels:** art, polish
**Description:**
Review and coordinate all art assets used in the game. Ensure visual consistency across all game elements. Optimize sprites and textures for performance.

### Issue 20: Implement zombie attack mechanics and animations
**Assignee:** Team Member 3
**Labels:** feature, enemy
**Description:**
Add attack mechanics for zombies to damage the player. Implement appropriate animations for zombie attacks. Add cooldown and range checking for attacks.

### Issue 21: Add sound effects for weapons, zombies, and player
**Assignee:** Team Member 3
**Labels:** feature, audio
**Description:**
Implement sound effects for weapon firing, reloading, and impacts. Add zombie sound effects for movement, attacks, and death. Include player sound effects for damage and healing.

### Issue 22: Implement basic music system
**Assignee:** Team Member 3
**Labels:** feature, audio
**Description:**
Add background music to the game. Implement volume control and muting options. Create different music tracks for menu and gameplay.

### Issue 23: Create simple visual effects for impacts and damage
**Assignee:** Team Member 3
**Labels:** feature, polish
**Description:**
Implement visual effects for weapon impacts, zombie deaths, and player damage. Add particle effects for blood splatter and bullet impacts. Ensure effects are optimized for performance.

### Issue 24: Integration and testing
**Assignee:** All Team Members
**Labels:** testing, integration
**Description:**
Integrate all components and systems. Test the game thoroughly for bugs and issues. Ensure all features work together seamlessly. Fix any integration issues that arise.

### Issue 25: Final adjustments and balance
**Assignee:** All Team Members
**Labels:** polish, balance
**Description:**
Make final adjustments to game balance, difficulty, and pacing. Tweak player movement, weapon damage, and zombie spawning. Ensure the game is challenging but fair.