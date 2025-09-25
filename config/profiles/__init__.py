"""
Profiles system for configurable data processing and language support.

This package intentionally avoids importing specific profiles at module import time
to ensure each profile can operate independently. Use `ProfileFactory` to create
the active profile.
"""

from .base_profile import BaseProfile
from .profile_factory import ProfileFactory

# Alias for backward compatibility with text2query components
DataProfile = BaseProfile

__all__ = ['BaseProfile', 'DataProfile', 'ProfileFactory']
