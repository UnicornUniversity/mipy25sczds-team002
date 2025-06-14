# Deadlock - Development Guidelines

This document outlines the development guidelines and best practices for the Deadlock project. Following these guidelines will ensure clean code, maintainable architecture, and efficient collaboration during the 2-day development timeline.

## Table of Contents
1. [Code Organization](#code-organization)
2. [Naming Conventions](#naming-conventions)
3. [Documentation Standards](#documentation-standards)
4. [Error Handling](#error-handling)
5. [Testing Approach](#testing-approach)
6. [Git Workflow](#git-workflow)
7. [Performance Considerations](#performance-considerations)
8. [Game-Specific Best Practices](#game-specific-best-practices)

## Code Organization

### Package Structure
Maintain the established package structure:
```
src/
├── entities/       # Game entities (player, zombies, items)
├── game/           # Core game mechanics and state management
├── systems/        # Game systems (collision, weapons, UI, etc.)
├── utils/          # Utility functions and constants
└── main.py         # Main entry point
```

### Module Responsibilities
- **entities/**: Contains all game objects that exist in the game world
  - Each entity should be in its own file (e.g., `player.py`, `zombie.py`)
  - Use inheritance from a base `Entity` class
  - Keep entity logic focused on the entity itself

- **game/**: Contains core game mechanics
  - `game_state.py`: Manages game states (menu, gameplay, game over)
  - `settings.py`: Game configuration and settings
  - `map_generator.py`: Map generation logic

- **systems/**: Contains game systems that operate on entities
  - Each system should be in its own file
  - Systems should be modular and focused on a single responsibility
  - Systems should not directly depend on each other

- **utils/**: Contains helper functions and constants
  - `constants.py`: Game constants (screen size, colors, etc.)
  - Helper modules should be focused on a specific type of utility

### Dependency Management
- Avoid circular dependencies
- Use dependency injection where appropriate
- Keep imports at the top of the file
- Group imports in the following order:
  1. Standard library imports
  2. Third-party library imports (e.g., pygame)
  3. Local application imports

## Naming Conventions

### General Naming
- Use descriptive names that reflect the purpose of the variable, function, or class
- Avoid abbreviations unless they are widely understood
- Be consistent with naming across the codebase

### Python-Specific Conventions
- **Classes**: Use `CamelCase` (e.g., `Player`, `ZombieSpawner`)
- **Functions and Methods**: Use `snake_case` (e.g., `update_position`, `handle_collision`)
- **Variables**: Use `snake_case` (e.g., `player_health`, `zombie_speed`)
- **Constants**: Use `UPPER_SNAKE_CASE` (e.g., `SCREEN_WIDTH`, `MAX_ZOMBIES`)
- **Private Methods/Variables**: Prefix with underscore (e.g., `_calculate_damage`)

### Game-Specific Naming
- **Entity Classes**: Name after the entity they represent (e.g., `Player`, `Zombie`)
- **System Classes**: Name after the system they implement (e.g., `CollisionSystem`, `AudioManager`)
- **State Classes**: Use the suffix "State" (e.g., `MenuState`, `GameplayState`)

## Documentation Standards

### Code Comments
- Use docstrings for all classes, methods, and functions
- Follow the Google docstring format:
```python
def function_name(param1, param2):
    """Short description of function.

    Longer description if needed.

    Args:
        param1: Description of param1
        param2: Description of param2

    Returns:
        Description of return value

    Raises:
        ExceptionType: When and why this exception is raised
    """
    # Function implementation
```

- Use inline comments sparingly and only when necessary to explain complex logic
- Keep comments up-to-date with code changes

### README and Documentation
- Keep the README.md up-to-date with installation and usage instructions
- Document design decisions and architecture in the appropriate documentation files
- Update documentation when making significant changes

## Error Handling

### Exception Handling
- Use specific exception types rather than catching all exceptions
- Handle exceptions at the appropriate level
- Log exceptions with useful information
- Don't suppress exceptions without good reason

### Defensive Programming
- Validate input parameters
- Check for edge cases
- Use assertions for debugging and to verify assumptions
- Fail fast and provide clear error messages

## Testing Approach

Given the 2-day timeline, focus on efficient testing:

### Manual Testing
- Test each feature immediately after implementation
- Create test scenarios for common gameplay situations
- Focus on critical systems (collision, combat, scoring)

### Integration Testing
- Test interactions between systems at the end of Day 1
- Ensure all team members test the integrated build
- Verify that systems work together as expected

### Final Playability Testing
- Conduct a group playtesting session at the end of Day 2
- Focus on identifying critical bugs and gameplay issues
- Make quick adjustments based on immediate feedback

## Git Workflow

### Branching Strategy
- `main` branch should always be in a deployable state
- Create feature branches for each task (e.g., `feature/player-movement`)
- Use pull requests for code review before merging

### Commit Guidelines
- Write clear, concise commit messages
- Use present tense ("Add feature" not "Added feature")
- Reference task numbers in commit messages when applicable
- Make small, focused commits rather than large, sweeping changes

### Collaboration
- Pull and merge changes frequently to avoid conflicts
- Communicate with team members when working on related areas
- Resolve conflicts promptly

## Performance Considerations

### Pygame-Specific Optimizations
- Use sprite groups for efficient rendering
- Limit the number of active entities based on screen visibility
- Use dirty rect animation for efficiency
- Avoid creating new objects every frame

### General Optimizations
- Profile code to identify bottlenecks
- Use appropriate data structures for the task
- Limit expensive operations (e.g., pathfinding) to necessary entities
- Consider using spatial partitioning for collision detection

## Game-Specific Best Practices

### Entity Management
- Use a central entity manager to track all game entities
- Implement a consistent update/render pattern for all entities
- Use composition over inheritance where appropriate
- Keep entity logic separate from rendering logic

### State Management
- Use the state pattern for game states
- Keep state transitions clean and explicit
- Ensure states can be easily added or modified

### Input Handling
- Centralize input handling
- Support both keyboard and mouse input
- Make controls configurable where possible
- Implement input buffering for responsive controls

### Resource Management
- Load assets at startup or level load, not during gameplay
- Implement a resource cache to avoid reloading assets
- Properly dispose of resources when no longer needed
- Use a sprite manager for efficient sprite handling

### Game Loop
- Maintain a consistent game loop with fixed time steps
- Separate update logic from rendering
- Use delta time for smooth movement
- Cap frame rate to avoid excessive CPU usage

---

By following these guidelines, the team can maintain clean, maintainable code while working efficiently within the 2-day development timeline. Remember that the primary goal is to create a functional game, so prioritize essential features and clean implementation over perfect code.
