import pygame
import os
import random
from typing import Dict, Optional


class SoundManager:
    """Unified sound manager for all audio (music, effects, etc.)"""

    def __init__(self):
        """Initialize the sound manager"""
        # Initialize pygame mixer if not already initialized
        if not pygame.mixer.get_init():
            pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)

        # Volume settings
        self.master_volume = 0.7
        self.music_volume = 0.3
        self.sfx_volume = 0.8

        # Current music state
        self.current_music = None
        self.music_playing = False
        self.music_paused = False

        # Sound cache - loads all sounds at startup
        self.sounds: Dict[str, pygame.mixer.Sound] = {}

        # Sound groups for cycling (e.g., hit_flesh_1, hit_flesh_2, hit_flesh_3)
        self.sound_groups: Dict[str, list] = {}

        # Load all sounds
        self._load_all_sounds()
        self._organize_sound_groups()

    def _load_all_sounds(self):
        """Load all sounds from assets/sounds directory recursively"""
        sounds_dir = "../assets/sounds"  # Opravená cesta

        if not os.path.exists(sounds_dir):
            print(f"Warning: Sounds directory '{sounds_dir}' not found.")
            return

        # Walk through all subdirectories
        for root, dirs, files in os.walk(sounds_dir):
            for filename in files:
                if filename.lower().endswith(('.wav', '.mp3', '.ogg')):
                    file_path = os.path.join(root, filename)

                    # Create sound name from file path relative to sounds_dir
                    relative_path = os.path.relpath(file_path, sounds_dir)
                    sound_name = relative_path.replace(os.sep, '_').replace('.', '_')
                    # Remove file extension from name
                    sound_name = '_'.join(sound_name.split('_')[:-1])

                    try:
                        self.sounds[sound_name] = pygame.mixer.Sound(file_path)
                        print(f"Loaded sound: {sound_name} <- {relative_path}")
                    except pygame.error as e:
                        print(f"Failed to load sound {file_path}: {e}")

        print(f"Total sounds loaded: {len(self.sounds)}")

    def _organize_sound_groups(self):
        """Organize sounds into groups for random/cycling playback"""
        # Group sounds by base name (e.g., hit_flesh_1, hit_flesh_2 -> hit_flesh group)
        for sound_name in self.sounds.keys():
            # Check if sound name ends with a number
            parts = sound_name.split('_')
            if len(parts) >= 2 and parts[-1].isdigit():
                # Remove the number to get base name
                base_name = '_'.join(parts[:-1])

                if base_name not in self.sound_groups:
                    self.sound_groups[base_name] = []

                self.sound_groups[base_name].append(sound_name)

        # Sort each group for consistent ordering
        for group in self.sound_groups.values():
            group.sort()

        print(f"Sound groups created: {list(self.sound_groups.keys())}")

    def play_sound(self, sound_name: str, volume: Optional[float] = None) -> bool:
        """Play a sound effect

        Args:
            sound_name (str): Name of the sound (e.g., 'weapons_pistol', 'effects_hit_flesh')
            volume (float, optional): Volume override for this sound (0.0 to 1.0)

        Returns:
            bool: True if sound was played successfully
        """
        # Check if this is a grouped sound (e.g., effects_hit_flesh)
        if sound_name in self.sound_groups:
            # Play a random sound from the group
            actual_sound_name = random.choice(self.sound_groups[sound_name])
        else:
            actual_sound_name = sound_name

        if actual_sound_name not in self.sounds:
            print(f"Sound not found: {sound_name} (tried: {actual_sound_name})")
            print(f"Available sounds: {list(self.sounds.keys())}")
            print(f"Available groups: {list(self.sound_groups.keys())}")
            return False

        try:
            sound = self.sounds[actual_sound_name]

            # Set volume
            if volume is not None:
                sound.set_volume(volume * self.master_volume)
            else:
                sound.set_volume(self.sfx_volume * self.master_volume)

            sound.play()
            return True

        except pygame.error as e:
            print(f"Failed to play sound {actual_sound_name}: {e}")
            return False

    def play_random_sound(self, base_name: str, volume: Optional[float] = None) -> bool:
        """Play a random sound from a group

        Args:
            base_name (str): Base name of the sound group (e.g., 'effects_hit_flesh')
            volume (float, optional): Volume override for this sound

        Returns:
            bool: True if sound was played successfully
        """
        return self.play_sound(base_name, volume)

    def play_music(self, music_name: str, loop: bool = True, fade_in: float = 0.0) -> bool:
        """Play background music using pygame.mixer.music

        Args:
            music_name (str): Name of the music (e.g., 'music_menu', 'music_boss_trance')
            loop (bool): Whether to loop the music
            fade_in (float): Fade in time in seconds

        Returns:
            bool: True if music started successfully
        """
        # Stop current music first
        if self.music_playing:
            self.stop_music()

        if music_name not in self.sounds:
            print(f"Music not found: {music_name}")
            return False

        try:
            # For music, we need to load the actual file path, not the Sound object
            # Find the original file path
            sounds_dir = "../assets/sounds"  # Opravená cesta
            for root, dirs, files in os.walk(sounds_dir):
                for filename in files:
                    if filename.lower().endswith(('.wav', '.mp3', '.ogg')):
                        file_path = os.path.join(root, filename)
                        relative_path = os.path.relpath(file_path, sounds_dir)
                        sound_name_check = relative_path.replace(os.sep, '_').replace('.', '_')
                        sound_name_check = '_'.join(sound_name_check.split('_')[:-1])

                        if sound_name_check == music_name:
                            # Load and play with pygame.mixer.music
                            pygame.mixer.music.load(file_path)
                            pygame.mixer.music.set_volume(self.music_volume * self.master_volume)

                            if fade_in > 0:
                                pygame.mixer.music.play(-1 if loop else 0, fade_ms=int(fade_in * 1000))
                            else:
                                pygame.mixer.music.play(-1 if loop else 0)

                            self.current_music = music_name
                            self.music_playing = True
                            self.music_paused = False

                            print(f"Playing music: {music_name}")
                            return True

            print(f"Music file not found for: {music_name}")
            return False

        except pygame.error as e:
            print(f"Failed to play music {music_name}: {e}")
            return False

    def stop_music(self, fade_out: float = 0.0):
        """Stop the currently playing music"""
        if not self.music_playing:
            return

        try:
            if fade_out > 0:
                pygame.mixer.music.fadeout(int(fade_out * 1000))
            else:
                pygame.mixer.music.stop()
        except pygame.error:
            pass

        self.current_music = None
        self.music_playing = False
        self.music_paused = False
        print("Music stopped")

    def pause_music(self):
        """Pause the currently playing music"""
        if self.music_playing and not self.music_paused:
            try:
                pygame.mixer.music.pause()
                self.music_paused = True
                print("Music paused")
            except pygame.error:
                pass

    def resume_music(self):
        """Resume the paused music"""
        if self.music_playing and self.music_paused:
            try:
                pygame.mixer.music.unpause()
                self.music_paused = False
                print("Music resumed")
            except pygame.error:
                pass

    def set_master_volume(self, volume: float):
        """Set master volume for all audio"""
        self.master_volume = max(0.0, min(1.0, volume))

        # Update music volume if playing
        if self.music_playing:
            try:
                pygame.mixer.music.set_volume(self.music_volume * self.master_volume)
            except pygame.error:
                pass

        print(f"Master volume set to: {self.master_volume:.1f}")

    def set_music_volume(self, volume: float):
        """Set music volume"""
        self.music_volume = max(0.0, min(1.0, volume))

        if self.music_playing:
            try:
                pygame.mixer.music.set_volume(self.music_volume * self.master_volume)
            except pygame.error:
                pass

        print(f"Music volume set to: {self.music_volume:.1f}")

    def set_sfx_volume(self, volume: float):
        """Set sound effects volume"""
        self.sfx_volume = max(0.0, min(1.0, volume))
        print(f"SFX volume set to: {self.sfx_volume:.1f}")

    def get_available_sounds(self) -> list:
        """Get list of all available sounds"""
        return list(self.sounds.keys())

    def get_available_groups(self) -> list:
        """Get list of all available sound groups"""
        return list(self.sound_groups.keys())

    def update(self, dt: float):
        """Update the sound manager"""
        # Check if music has stopped playing
        if self.music_playing and not self.music_paused:
            try:
                if not pygame.mixer.music.get_busy():
                    self.music_playing = False
                    self.current_music = None
                    print("Music finished playing")
            except pygame.error:
                pass


# Global sound manager instance - PŘIDÁNO!
sound_manager = SoundManager()

# Convenience aliases for backward compatibility
music_manager = sound_manager