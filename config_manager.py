import json
import os

class ConfigManager:
    def __init__(self, config_file="config.json"):
        self.config_file = config_file
        self.default_config = {
            "reminder_mode": "blur", # "blur" or "indicator"
            "baseline_score": 0.0,   # Standard posture score
            "slouch_score": 0.0,     # Severe slouch score (optional calibration)
            "is_calibrated": False,
            "dead_zone_ratio": 0.90, # Default drop ratio for dead zone (if only baseline is used)
            "max_slouch_ratio": 0.70 # Default drop ratio for max slouch (if only baseline is used)
        }
        self.config = self.load_config()

    def load_config(self):
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # Merge with default config to ensure all keys exist
                    config = self.default_config.copy()
                    config.update(data)
                    return config
            except Exception as e:
                print(f"Error loading config: {e}")
                return self.default_config.copy()
        else:
            return self.default_config.copy()

    def save_config(self):
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving config: {e}")

    def get(self, key):
        return self.config.get(key, self.default_config.get(key))

    def set(self, key, value):
        self.config[key] = value
        self.save_config()

    def reset_to_defaults(self):
        self.config = self.default_config.copy()
        self.save_config()
