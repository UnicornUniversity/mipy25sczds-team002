# Deadlock - Game Design Document

## Game Overview
- Top-down zombie survival game with pixel art graphics
- Player's objective is to survive as long as possible and achieve the highest score
- Game takes place on a square map with buildings, obstacles, and resources
- Increasing difficulty over time to challenge the player

> **Note:** This document has been updated to reflect a more realistic scope for a 3-person team with a 2-day development timeline. Features marked with "(Optional)" are lower priority and should only be implemented if time permits.

## Core Gameplay Mechanics

### Player Movement and Controls
- Top-down movement using WASD or arrow keys
- Mouse aiming for weapons
- Left mouse button to shoot
- R key to reload weapons
- E key to interact with objects (pick up items, open doors)
- Space bar for dodge roll (with cooldown) (Optional)

### Survival Elements
- Player has limited health (HP)
- Health decreases when attacked by zombies
- Health can be restored by finding health packs
- Score increases over time and by killing zombies
- Game ends when player's health reaches zero

### Map and Environment
- Procedurally generated square map
- Various environment elements:
  - Buildings (can be entered) (Optional)
  - Obstacles (trees, cars, barricades)
  - Destructible objects (Optional)
  - Loot containers (ammo boxes, supply crates)
- Limited visibility at night or in buildings (Optional)
- Map boundaries that prevent player from leaving the area

## Entities

### Player
- Customizable character with different sprites (Optional)
- Health system with visual indicator
- Inventory for weapons and items
- Stamina system for special movements (dodge roll) (Optional)

### Zombies
- Basic zombie: Slow movement, medium health, medium damage
- Runner zombie: Fast movement, low health, low damage (Optional)
- Tank zombie: Very slow movement, high health, high damage (Optional)
- Boss zombie (rare): Special abilities, very high health, high damage (Optional)
- Zombies follow player using pathfinding
- Zombies can break through weak obstacles (Optional)
- Zombie spawning increases in frequency and difficulty over time

### Items and Pickups
- Health packs: Restore player health
- Ammo: Replenish weapon ammunition
- Weapons: New weapons with different characteristics
- Power-ups: Temporary boosts (speed, damage, invincibility) (Optional)

## Weapons System

### Weapon Types
- Pistol: Balanced damage/fire rate, unlimited ammo
- Shotgun: High damage at close range, slow reload (Optional)
- Assault Rifle: Rapid fire, medium damage (Optional)
- Sniper Rifle: High damage, slow fire rate, high accuracy (Optional)
- Melee Weapons: No ammo required, limited range

### Weapon Mechanics
- Limited ammunition for all weapons except melee
- Different reload times for different weapons
- Weapon switching with number keys or scroll wheel
- Different sound effects and visual feedback for each weapon (Optional)
- Weapon upgrades or modifications found throughout the game (Optional)

## Difficulty Scaling

### Time-Based Progression
- Zombie spawn rate increases over time
- Stronger zombie types appear as time progresses (Optional)
- Resources become scarcer over time
- Environmental hazards may appear (toxic zones, fires) (Optional)

### Score-Based Progression
- Higher scores trigger special events (zombie hordes) (Optional)
- Boss zombies appear at specific score thresholds (Optional)
- New areas of the map unlock at certain scores (Optional)
- Special challenges appear at score milestones (Optional)

## User Interface

### Active UI Elements
- Health bar: Visual representation of player's current health
- Ammo counter: Shows current ammo and total ammo for equipped weapon
- Score display: Current score prominently displayed
- Mini-map: Small map showing nearby zombies and important locations (Optional)
- Timer: Shows how long the player has survived

### Menu UI Elements
- Main Menu: Title, Start Game, Settings, High Scores, Exit
- Pause Menu: Resume, Settings, Return to Main Menu
- Game Over Screen: Final Score, Time Survived, Zombies Killed, Restart, Main Menu
- Settings Menu: Sound volume, Music volume, Graphics options, Controls (Optional)

### Visual Feedback
- Screen flash when taking damage
- Blood splatter effects for zombie kills (Optional)
- Visual cues for low health, low ammo
- Directional indicators for nearby zombies (Optional)

## Audio Design

### Sound Effects
- Weapon sounds (firing, reloading, empty)
- Zombie sounds (groaning, attacking, dying)
- Player sounds (footsteps, damage, healing) (Optional)
- Environmental sounds (doors, items, explosions) (Optional)

### Music
- Dynamic music system that changes based on game state (Optional)
- Calm music during exploration
- Intense music during combat or high-stress situations (Optional)
- Special music for boss encounters (Optional)
- Game over and victory themes

## Technical Requirements
- Built with Pygame
- Pixel art graphics style
- Efficient pathfinding for multiple zombies
- Collision detection system
- Particle effects system for visual feedback (Optional)
- Save/load system for high scores (Optional)
