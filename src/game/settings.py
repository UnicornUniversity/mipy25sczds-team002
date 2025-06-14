class Settings:
    def __init__(self):
        self.sound_enabled = True
        self.music_volume = 0.7
        self.sfx_volume = 0.8
        self.fullscreen = False
        self.difficulty = "normal"

    def save_settings(self, filename="settings.json"):
        import json
        settings_dict = {
            "sound_enabled": self.sound_enabled,
            "music_volume": self.music_volume,
            "sfx_volume": self.sfx_volume,
            "fullscreen": self.fullscreen,
            "difficulty": self.difficulty
        }
        with open(filename, 'w') as f:
            json.dump(settings_dict, f, indent=2)

    def load_settings(self, filename="settings.json"):
        import json
        try:
            with open(filename, 'r') as f:
                settings_dict = json.load(f)
                self.sound_enabled = settings_dict.get("sound_enabled", True)
                self.music_volume = settings_dict.get("music_volume", 0.7)
                self.sfx_volume = settings_dict.get("sfx_volume", 0.8)
                self.fullscreen = settings_dict.get("fullscreen", False)
                self.difficulty = settings_dict.get("difficulty", "normal")
        except FileNotFoundError:
            pass  # Use default