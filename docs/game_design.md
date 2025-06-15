# Deadlock - Implemented Features

## Game Overview
- Top-down zombie survival game with pixel art graphics
- Player's objective is to survive as long as possible and achieve the highest score
- Game takes place on a procedurally generated map with obstacles
- Increasing difficulty over time to challenge the player

## Core Gameplay Mechanics

### Player Movement and Controls
- Top-down movement using WASD or arrow keys
- Mouse aiming for weapons
- Left mouse button to shoot
- R key to reload weapons
- Q/E keys to cycle through weapons
- Number keys (1-5) to switch weapons directly

### Survival Elements
- Player has limited health (HP)
- Health decreases when attacked by zombies
- Health can be restored by finding health packs
- Score increases over time and by killing zombies
- Game ends when player's health reaches zero

### Map and Environment
- Procedurally generated square map
- Various environment elements:
  - Obstacles (objects that slow movement)
  - Map boundaries that prevent player from leaving the area

## Entities

### Player
- Health system with visual indicator
- Weapon inventory system with up to 5 weapons
- Different sprites based on equipped weapon
- Footstep sounds during movement

### Zombies
- Basic zombie: Balanced speed, health, and damage
- Fast zombie: Higher speed, lower health, lower damage
- Tough zombie: Lower speed, higher health, higher damage
- Zombies follow player using basic pathfinding
- Zombies make groaning sounds and attack sounds
- Zombies have different visual appearances (color tints)
- Stuck detection system to prevent zombies from getting trapped

### Items and Pickups
- Health packs: Restore player health
- Ammo: Provides infinite ammo for a limited time
- Weapons: New weapons with different characteristics
- Power-ups:
  - Speed Boost: Increases player movement speed
  - Damage Boost: Increases weapon damage
  - Health Regeneration: Regenerates health over time
  - Invincibility: Makes player invulnerable
  - Rapid Fire: Increases weapon fire rate

## Weapons System

### Weapon Types
- Pistol: Balanced damage/fire rate, unlimited ammo
- Shotgun: High damage at close range, slow reload, fires multiple pellets
- Assault Rifle: Rapid fire, medium damage
- Sniper Rifle: High damage, slow fire rate, high accuracy
- Bazooka: Explosive damage, very slow fire rate

### Weapon Mechanics
- Limited ammunition for all weapons
- Different reload times for different weapons
- Weapon switching with number keys or Q/E
- Different sound effects for each weapon
- Visual muzzle flash effects when shooting
- Explosive weapons cause area damage

## Difficulty Scaling
- Zombie spawn rate increases over time
- Stronger zombie types appear as time progresses

## User Interface

### Active UI Elements
- Health bar: Visual representation of player's current health with color gradient
- Weapon display: Shows current weapon, ammo, and reload status
- Weapon inventory: Visual display of available weapons with active weapon highlighted
- Score display: Current score prominently displayed
- Notification system: Displays temporary messages for pickups, damage, etc.

### Menu UI Elements
- Main Menu: Title, Start Game, High Scores, Exit
- Game Over Screen: Final Score, Name Input, Restart, Main Menu
- High Scores Screen: Displays top 10 scores with names and dates

### Visual Feedback
- Blood splatter effects for zombie kills
- Visual cues for low health (health bar color)
- Muzzle flash when shooting
- Explosion effects for explosive weapons

## Audio Design

### Sound Effects
- Weapon sounds (firing for different weapon types)
- Zombie sounds (groaning, attacking)
- Player sounds (footsteps)
- Environmental sounds (explosions)

### Music
- Menu music
- Gameplay music
- Volume control for both music and sound effects
- Music and sound can be toggled on/off

## Technical Features
- Built with Pygame
- Pixel art graphics style
- Collision detection system
- Animation system for visual effects
- Save/load system for high scores
- Sprite loading and management system