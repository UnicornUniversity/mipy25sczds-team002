# Music System Documentation

## Overview

The music system provides background music and sound effects management for the Deadlock game. It supports different music categories, volume control, and muting options as specified in task #22.

## Features

### Background Music
- **Menu Music**: Plays when in the main menu
- **Gameplay Music**: Plays during active gameplay
- **Intense Music**: For high-stress situations (future implementation)
- **Victory Music**: For victory screens (future implementation)
- **Game Over Music**: For game over screens (future implementation)

### Volume Control
- **Music Volume**: Adjustable from 0% to 100%
- **Sound Effects Volume**: Separate control for SFX
- **Real-time Adjustment**: Changes apply immediately

### Muting Options
- **Toggle Music**: Enable/disable background music
- **Toggle Sound Effects**: Enable/disable all sound effects
- **Persistent Settings**: Settings are maintained during gameplay

## Implementation

### Core Components

#### MusicManager Class
Located in `src/systems/audio.py`, this is the main class that handles all music operations:

```python
class MusicManager:
    - music_volume: float (0.0 to 1.0)
    - sfx_volume: float (0.0 to 1.0)
    - music_enabled: bool
    - sfx_enabled: bool
    - current_track: str
    - current_category: str
    - is_playing: bool
    - is_paused: bool
```

#### Key Methods
- `play_music(category, loop, fade_in)`: Play music from specific category
- `stop_music(fade_out)`: Stop current music with optional fade out
- `set_music_volume(volume)`: Set music volume (0.0-1.0)
- `set_sfx_volume(volume)`: Set sound effects volume (0.0-1.0)
- `toggle_music()`: Toggle music on/off
- `toggle_sfx()`: Toggle sound effects on/off

### Music Categories

The system organizes music into categories stored in separate directories:

```
assets/sounds/music/
├── menu/           # Menu background music
├── gameplay/       # Gameplay background music
├── intense/        # High-stress situation music
├── victory/        # Victory celebration music
└── game_over/      # Game over music
```

### Supported Audio Formats
- **MP3**: Primary format for music tracks
- **OGG**: Alternative format with good compression
- **WAV**: Uncompressed format for high quality

### Sound Effects
Sound effects are loaded from category-specific directories:

```
assets/sounds/
├── weapons/        # Weapon firing, reloading sounds
├── player/         # Player movement, damage sounds
└── zombies/        # Zombie groaning, attack sounds
```

## Controls

### Keyboard Controls
- **M**: Toggle music on/off
- **N**: Toggle sound effects on/off
- **[**: Decrease music volume by 10%
- **]**: Increase music volume by 10%

These controls work in both menu and gameplay states.

## Integration

### Game States Integration

#### MenuState
- Automatically starts menu music when entered
- Displays current music status and controls
- Shows real-time volume levels

#### GameplayState
- Automatically starts gameplay music when entered
- Music controls available during gameplay
- Debug mode shows detailed music information

### Main Game Loop
The music manager is updated in the main game loop:

```python
# Update music manager
music_manager.update(dt)
```

## Placeholder System

When no actual music files are found, the system creates placeholder tracks:
- `placeholder_menu`
- `placeholder_gameplay_1`
- `placeholder_gameplay_2`
- `placeholder_intense`
- `placeholder_victory`
- `placeholder_game_over`

This ensures the system works even without audio files, making development and testing easier.

## Performance Considerations

### Lazy Loading
- Music files are loaded only when needed
- Sound effects are cached for quick access
- Minimal memory footprint when no audio files present

### Error Handling
- Graceful fallback when audio files are missing
- Error logging for debugging
- No crashes due to audio system failures

## Future Enhancements

### Dynamic Music System
- Music intensity based on zombie count
- Smooth transitions between music categories
- Adaptive volume based on game events

### Advanced Audio Features
- 3D positional audio for sound effects
- Audio filters and effects
- Custom audio mixing

### Settings Integration
- Save/load audio preferences
- Audio quality settings
- Custom key bindings for audio controls

## Usage Examples

### Playing Music
```python
from systems.audio import play_menu_music, play_gameplay_music

# Start menu music
play_menu_music()

# Start gameplay music
play_gameplay_music()
```

### Volume Control
```python
from systems.audio import set_music_volume, set_sfx_volume

# Set music volume to 50%
set_music_volume(0.5)

# Set sound effects volume to 80%
set_sfx_volume(0.8)
```

### Toggle Controls
```python
from systems.audio import toggle_music, toggle_sfx

# Toggle music on/off
toggle_music()

# Toggle sound effects on/off
toggle_sfx()
```

## Troubleshooting

### No Music Playing
1. Check if music files exist in `assets/sounds/music/`
2. Verify audio file formats are supported (.mp3, .ogg, .wav)
3. Check if music is enabled (press M to toggle)
4. Verify volume is not set to 0 (use [ and ] keys)

### Performance Issues
1. Reduce number of simultaneous sound effects
2. Use compressed audio formats (OGG recommended)
3. Lower audio quality settings if needed

### Audio Not Loading
1. Check file permissions
2. Verify pygame mixer initialization
3. Check console output for error messages

## Technical Details

### Audio Initialization
```python
pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
```

### File Structure
- Music files: `assets/sounds/music/{category}/`
- Sound effects: `assets/sounds/{category}/`
- Supported extensions: .mp3, .ogg, .wav

### Memory Management
- Sound effects are cached in memory for performance
- Music tracks are loaded on-demand
- Automatic cleanup of finished effects

## Conclusion

The music system successfully implements all requirements from task #22:
- ✅ Background music for different game states
- ✅ Volume control for music and sound effects
- ✅ Muting options for both music and SFX
- ✅ Different music tracks for menu and gameplay
- ✅ Real-time controls and feedback
- ✅ Robust error handling and fallback system

The system is designed to be extensible and can easily accommodate additional music categories and advanced audio features in the future. 