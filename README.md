# Deadlock

A top-down zombie survival game built with Pygame where players must survive as long as possible against increasingly difficult waves of zombies.

## Game Overview

This game is a workshop project for Python Essentials made by team 2. It features:

- Top-down pixel art graphics
- Procedurally generated maps
- Multiple zombie types with AI pathfinding
- Weapon system with different guns and ammo management
- Score-based progression and difficulty scaling
- Dynamic UI and audio feedback

## Project Documentation

The following documents outline the game design and development plan:

- [Game Design Document](docs/game_design.md) - Detailed description of game mechanics, features, and systems
- [Task Distribution](docs/task_distribution.md) - Division of responsibilities among team members
- [Implementation Plan](docs/implementation_plan.md) - Technical roadmap for development

## Getting Started

### Prerequisites

- Python 3.8+
- Pygame

### Installation

1. Clone the repository
```
git clone https://github.com/yourusername/mipy25sczds-team002.git
cd mipy25sczds-team002
```

2. Install dependencies
```
pip install -r requirements.txt
```

3. Run the game
```
python src/main.py
```

## Development

The project follows a modular structure with clear separation of concerns:

- `src/entities/` - Game entities (player, zombies, items)
- `src/game/` - Game state and core mechanics
- `src/systems/` - Game systems (collision, weapons, UI)
- `src/utils/` - Utility functions and constants

Refer to the [Implementation Plan](docs/implementation_plan.md) for details on the code structure and integration points.

## Contributing

1. Review the [Task Distribution](docs/task_distribution.md) to understand your responsibilities
2. Create a branch for your feature
3. Implement your assigned tasks
4. Submit a pull request for review
5. Participate in weekly integration meetings

## License

This project is licensed under the MIT License - see the LICENSE file for details.
