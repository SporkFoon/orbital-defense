# Orbital Defense

A space-themed tower defense game where players must protect their planetary base from waves of incoming alien invaders

## Game Concept

Orbital Defense is a strategic tower defense game set in space. Players defend their home planet from waves of alien invaders by strategically placing defensive structures in orbit. Each wave becomes progressively more challenging

![Gameplay Screenshot](screenshots/gameplay/gameplay.png)

## Features

- Orbital placement system: Players place defenses in circular orbits around their planet
- Multiple defense types: Laser turrets and resource collectors (more planned)
- Resource management: Players must balance between building defenses and collecting resources
- Wave-based gameplay: Increasingly difficult waves of enemies
- Comprehensive statistics tracking: Player performance metrics visualized after gameplay

### Instructions

1. Clone the repository:
   ```
   git clone https://github.com/SporkFoon/orbital-defense.git
   cd orbital-defense
   ```

2. Install PyGame if you don't have it:
   ```
   pip install pygame
   ```

3. Run the game:
   ```
   python main.py
   ```

## Controls

- `1` - Select Laser Turret
- `2` - Select Resource Collector
- `P` - Toggle placement mode
- `Left Mouse Button` - Place selected defense (in placement mode)
- `Space` - Start next wave
- `H` - Toggle help overlay
- `Esc` - Quit game


## Game Structure

- `main.py` - Entry point for the game
- `constants.py` - Game constants, colors, and settings
- `game_objects.py` - Base game object classes
- `defenses.py` - Defense tower implementations
- `projectiles.py` - Projectile mechanics
- `enemies.py` - Enemy types and behaviors
- `wave_manager.py` - Controls enemy wave generation
- `game_stats.py` - Statistics tracking and database functionality
- `ui_manager.py` - UI rendering and user interface
- `game_controller.py` - Main game logic
- `stats_display.py` - Statistics visualization dashboard

## Statistics and Analysis

After each game, detailed statistics are presented to help you analyze your performance

These statistics include:
- Defense placement heatmaps showing your strategic preferences
![placement heatmaps](screenshots/visualization/heatmap.png)
- Resource collection trends across games
![Resource collection](screenshots/visualization/resourcesgraph.png)
- Enemy survival analysis
![survival analysis](screenshots/visualization/enemysurvival.png)
- Overall performance metrics
![Statistics Summary](screenshots/visualization/stats.png)

[Youtube Presentation](https://youtu.be/HgvrTTnGMPg)