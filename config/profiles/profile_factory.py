#!/usr/bin/env python3
"""
Profile factory for loading and managing data processing profiles.
"""

from typing import Dict, Type
import importlib
from pathlib import Path
from .base_profile import BaseProfile


class ProfileFactory:
    """Factory for creating and managing profiles with dynamic discovery."""

    # Cache for discovered profiles
    _profile_import_map: Dict[str, tuple[str, str]] = None

    @classmethod
    def _discover_profiles(cls) -> Dict[str, tuple[str, str]]:
        """Discover available profiles by scanning the profiles directory."""
        if cls._profile_import_map is not None:
            return cls._profile_import_map
        
        profiles = {}
        profiles_dir = Path(__file__).parent
        
        for profile_dir in profiles_dir.iterdir():
            if (profile_dir.is_dir() and 
                profile_dir.name not in ['__pycache__', 'common_test_utils'] and
                (profile_dir / 'profile_config.py').exists()):
                
                profile_name = profile_dir.name
                module_path = f"config.profiles.{profile_name}.profile_config"
                
                # Try to determine class name dynamically
                # Convert profile_name to PascalCase (e.g., default_profile -> DefaultProfile)
                class_name = ''.join(word.capitalize() for word in profile_name.split('_'))
                
                profiles[profile_name] = (module_path, class_name)
        
        cls._profile_import_map = profiles
        return profiles

    @classmethod
    def get_available_profiles(cls) -> list[str]:
        """Return profile names that can be successfully imported."""
        available: list[str] = []
        profile_map = cls._discover_profiles()
        
        for name, (module_path, class_name) in profile_map.items():
            try:
                module = importlib.import_module(module_path)
                getattr(module, class_name)
                available.append(name)
            except Exception:
                # If a profile package is missing, skip it silently
                continue
        return available

    @classmethod
    def create_profile(cls, profile_name: str) -> BaseProfile:
        """Create a profile instance by name using lazy import."""
        profile_map = cls._discover_profiles()
        
        if profile_name not in profile_map:
            raise ValueError(
                f"Unknown profile: {profile_name}. Available profiles: {cls.get_available_profiles()}"
            )

        module_path, class_name = profile_map[profile_name]
        try:
            module = importlib.import_module(module_path)
            profile_class: Type[BaseProfile] = getattr(module, class_name)
        except Exception as e:
            raise ImportError(
                f"Failed to import profile '{profile_name}' from {module_path}.{class_name}: {e}"
            )
        return profile_class()

    @classmethod
    def register_profile(cls, name: str, module_path: str, class_name: str):
        """Register a new profile by module path and class name."""
        # Ensure the cache is initialized
        if cls._profile_import_map is None:
            cls._discover_profiles()
        cls._profile_import_map[name] = (module_path, class_name)
