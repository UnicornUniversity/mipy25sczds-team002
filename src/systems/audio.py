import pygame
import os
import random
from typing import Dict, Optional, List


class MusicManager:
    """Manages background music and sound effects for the game"""
    
    def __init__(self):
        """Initialize the music manager"""
        # Initialize pygame mixer if not already initialized
        if not pygame.mixer.get_init():
            pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
        
        # Music settings
        self.music_volume = 0.3
        self.sfx_volume = 0.8
        self.music_enabled = True
        self.sfx_enabled = True
        
        # Current music state
        self.current_track = None
        self.current_category = None
        self.is_playing = False
        self.is_paused = False
        
        # Music tracks organized by category
        self.music_tracks: Dict[str, List[str]] = {
            'menu': [],
            'gameplay': [],
            'intense': [],  # For high-stress situations
            'victory': [],
            'game_over': []
        }
        
        # Sound effects cache
        self.sound_effects: Dict[str, pygame.mixer.Sound] = {}
        
        # Load music tracks
        self._load_music_tracks()
        
        # Load sound effects
        self._load_sound_effects()
    
    def _load_music_tracks(self):
        """Load all music tracks from the assets/sounds/music directory"""
        music_dir = "assets/sounds/music"
        
        if not os.path.exists(music_dir):
            print(f"Warning: Music directory '{music_dir}' not found. Creating placeholder tracks.")
            self._create_placeholder_tracks()
            return
        
        # Define subdirectories for different music categories
        categories = ['menu', 'gameplay', 'intense', 'victory', 'game_over']
        
        for category in categories:
            category_dir = os.path.join(music_dir, category)
            if os.path.exists(category_dir):
                # Load all music files from this category
                for filename in os.listdir(category_dir):
                    if filename.lower().endswith(('.mp3', '.ogg', '.wav')):
                        track_path = os.path.join(category_dir, filename)
                        self.music_tracks[category].append(track_path)
                        print(f"Loaded music track: {category}/{filename}")
        
        # If no tracks found, create placeholder tracks
        if not any(self.music_tracks.values()):
            self._create_placeholder_tracks()
    
    def _create_placeholder_tracks(self):
        """Create placeholder tracks when no music files are found"""
        print("Creating placeholder music tracks...")
        
        # For now, we'll use None as placeholders
        # In a real implementation, you could generate simple tones or use default pygame sounds
        self.music_tracks = {
            'menu': ['placeholder_menu'],
            'gameplay': ['placeholder_gameplay_1', 'placeholder_gameplay_2'],
            'intense': ['placeholder_intense'],
            'victory': ['placeholder_victory'],
            'game_over': ['placeholder_game_over']
        }
        
        print("Placeholder tracks created. Add real music files to assets/sounds/music/ for better experience.")
    
    def _load_sound_effects(self):
        """Load sound effects from the assets/sounds directory"""
        sounds_dir = "assets/sounds"
        
        if not os.path.exists(sounds_dir):
            print(f"Warning: Sounds directory '{sounds_dir}' not found.")
            return
        
        # Load sound effects from different categories
        sfx_categories = ['weapons', 'player', 'zombies']
        
        for category in sfx_categories:
            category_dir = os.path.join(sounds_dir, category)
            if os.path.exists(category_dir):
                for filename in os.listdir(category_dir):
                    if filename.lower().endswith(('.wav', '.ogg')):
                        sound_path = os.path.join(category_dir, filename)
                        try:
                            sound_name = f"{category}_{os.path.splitext(filename)[0]}"
                            self.sound_effects[sound_name] = pygame.mixer.Sound(sound_path)
                            print(f"Loaded sound effect: {sound_name}")
                        except pygame.error as e:
                            print(f"Failed to load sound {sound_path}: {e}")
    
    def play_music(self, category: str, loop: bool = True, fade_in: float = 0.0):
        """Play music from a specific category
        
        Args:
            category (str): Music category ('menu', 'gameplay', 'intense', etc.)
            loop (bool): Whether to loop the music
            fade_in (float): Fade in time in seconds
        """
        if not self.music_enabled or category not in self.music_tracks:
            return
        
        tracks = self.music_tracks[category]
        if not tracks:
            print(f"No tracks available for category: {category}")
            return
        
        # Stop current music if playing
        if self.is_playing:
            self.stop_music()
        
        # Select a random track from the category
        selected_track = random.choice(tracks)
        
        try:
            if selected_track.startswith('placeholder_'):
                # Handle placeholder tracks (no actual file)
                print(f"Playing placeholder track: {selected_track}")
                self.current_track = selected_track
                self.current_category = category
                self.is_playing = True
                return
            
            # Load and play the actual music file
            pygame.mixer.music.load(selected_track)
            
            # Set volume
            pygame.mixer.music.set_volume(self.music_volume)
            
            # Play with or without fade in
            if fade_in > 0:
                pygame.mixer.music.play(-1 if loop else 0, fade_ms=int(fade_in * 1000))
            else:
                pygame.mixer.music.play(-1 if loop else 0)
            
            self.current_track = selected_track
            self.current_category = category
            self.is_playing = True
            self.is_paused = False
            
            print(f"Playing music: {os.path.basename(selected_track)} from {category}")
            
        except pygame.error as e:
            print(f"Failed to play music {selected_track}: {e}")
    
    def stop_music(self, fade_out: float = 0.0):
        """Stop the currently playing music
        
        Args:
            fade_out (float): Fade out time in seconds
        """
        if not self.is_playing:
            return
        
        try:
            if fade_out > 0:
                pygame.mixer.music.fadeout(int(fade_out * 1000))
            else:
                pygame.mixer.music.stop()
        except pygame.error:
            pass
        
        self.current_track = None
        self.current_category = None
        self.is_playing = False
        self.is_paused = False
        
        print("Music stopped")
    
    def pause_music(self):
        """Pause the currently playing music"""
        if self.is_playing and not self.is_paused:
            try:
                pygame.mixer.music.pause()
                self.is_paused = True
                print("Music paused")
            except pygame.error:
                pass
    
    def resume_music(self):
        """Resume the paused music"""
        if self.is_playing and self.is_paused:
            try:
                pygame.mixer.music.unpause()
                self.is_paused = False
                print("Music resumed")
            except pygame.error:
                pass
    
    def set_music_volume(self, volume: float):
        """Set the music volume
        
        Args:
            volume (float): Volume level (0.0 to 1.0)
        """
        self.music_volume = max(0.0, min(1.0, volume))
        
        if self.is_playing:
            try:
                pygame.mixer.music.set_volume(self.music_volume)
            except pygame.error:
                pass
        
        print(f"Music volume set to: {self.music_volume:.1f}")
    
    def set_sfx_volume(self, volume: float):
        """Set the sound effects volume
        
        Args:
            volume (float): Volume level (0.0 to 1.0)
        """
        self.sfx_volume = max(0.0, min(1.0, volume))
        
        # Update volume for all loaded sound effects
        for sound in self.sound_effects.values():
            sound.set_volume(self.sfx_volume)
        
        print(f"SFX volume set to: {self.sfx_volume:.1f}")
    
    def toggle_music(self):
        """Toggle music on/off"""
        self.music_enabled = not self.music_enabled
        
        if not self.music_enabled and self.is_playing:
            self.pause_music()
        elif self.music_enabled and self.is_paused:
            self.resume_music()
        
        print(f"Music {'enabled' if self.music_enabled else 'disabled'}")
    
    def toggle_sfx(self):
        """Toggle sound effects on/off"""
        self.sfx_enabled = not self.sfx_enabled
        print(f"Sound effects {'enabled' if self.sfx_enabled else 'disabled'}")
    
    def play_sound(self, sound_name: str, volume: Optional[float] = None):
        """Play a sound effect
        
        Args:
            sound_name (str): Name of the sound effect
            volume (float, optional): Volume override for this sound
        """
        if not self.sfx_enabled or sound_name not in self.sound_effects:
            return
        
        try:
            sound = self.sound_effects[sound_name]
            
            if volume is not None:
                # Set volume and play
                sound.set_volume(max(0.0, min(1.0, volume)))
            
            sound.play()
                
        except pygame.error as e:
            print(f"Failed to play sound {sound_name}: {e}")
    
    def update(self, dt: float):
        """Update the music manager
        
        Args:
            dt (float): Time delta in seconds
        """
        # Check if music has stopped playing (for non-looping tracks)
        if self.is_playing and not self.is_paused:
            try:
                if not pygame.mixer.music.get_busy() and not self.current_track.startswith('placeholder_'):
                    # Music has finished, mark as not playing
                    self.is_playing = False
                    self.current_track = None
                    self.current_category = None
                    print("Music finished playing")
            except pygame.error:
                pass
    
    def get_status(self) -> Dict:
        """Get current music manager status
        
        Returns:
            Dict: Status information
        """
        return {
            'music_enabled': self.music_enabled,
            'sfx_enabled': self.sfx_enabled,
            'music_volume': self.music_volume,
            'sfx_volume': self.sfx_volume,
            'is_playing': self.is_playing,
            'is_paused': self.is_paused,
            'current_track': os.path.basename(self.current_track) if self.current_track else None,
            'current_category': self.current_category,
            'available_tracks': {cat: len(tracks) for cat, tracks in self.music_tracks.items()},
            'loaded_sounds': len(self.sound_effects)
        }


# Global music manager instance
music_manager = MusicManager()


# Convenience functions for easy access
def play_menu_music():
    """Play menu background music"""
    music_manager.play_music('menu', loop=True, fade_in=1.0)


def play_gameplay_music():
    """Play gameplay background music"""
    music_manager.play_music('gameplay', loop=True, fade_in=1.0)


def play_intense_music():
    """Play intense music for high-stress situations"""
    music_manager.play_music('intense', loop=True, fade_in=0.5)


def play_victory_music():
    """Play victory music"""
    music_manager.play_music('victory', loop=False)


def play_game_over_music():
    """Play game over music"""
    music_manager.play_music('game_over', loop=False)


def stop_music(fade_out: float = 1.0):
    """Stop current music with fade out"""
    music_manager.stop_music(fade_out)


def set_music_volume(volume: float):
    """Set music volume (0.0 to 1.0)"""
    music_manager.set_music_volume(volume)


def set_sfx_volume(volume: float):
    """Set sound effects volume (0.0 to 1.0)"""
    music_manager.set_sfx_volume(volume)


def toggle_music():
    """Toggle music on/off"""
    music_manager.toggle_music()


def toggle_sfx():
    """Toggle sound effects on/off"""
    music_manager.toggle_sfx()


def play_sound(sound_name: str, volume: Optional[float] = None):
    """Play a sound effect"""
    music_manager.play_sound(sound_name, volume)
