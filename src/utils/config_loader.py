"""
Configuration Loader
Loads and validates YAML configuration.
"""
import yaml
import sys
from pathlib import Path
from typing import Dict, Any

class ConfigLoader:
    @staticmethod
    def load(config_path: str = "config.yaml") -> Dict[str, Any]:
        path = Path(config_path)
        if not path.exists():
            raise FileNotFoundError(f"Configuration file not found: {path}")
        
        try:
            with open(path, "r", encoding="utf-8") as f:
                return yaml.safe_load(f) or {}
        except Exception as e:
            raise RuntimeError(f"Failed to parse config file: {e}")
