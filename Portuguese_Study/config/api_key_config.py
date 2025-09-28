"""
Simple API Key Configuration for Portuguese Study TTS System

Imports API keys from api_key_constants.py and provides helper functions.
"""

import os
from .api_key_constants import OPENAI_API_KEY, GEMINI_API_KEY

# ===========================================
# HELPER FUNCTIONS
# ===========================================

def get_api_key(provider: str):
    """Get API key for a provider."""
    if provider == 'openai':
        return OPENAI_API_KEY or os.getenv('OPENAI_API_KEY')
    elif provider == 'gemini':
        return GEMINI_API_KEY or os.getenv('GEMINI_API_KEY')
    else:
        raise ValueError(f"Unknown provider: {provider}")

def is_configured(provider: str) -> bool:
    """Check if API key is configured for a provider."""
    return get_api_key(provider) is not None

def get_configured_providers() -> list:
    """Get list of configured providers."""
    providers = []
    if is_configured('openai'):
        providers.append('openai')
    if is_configured('gemini'):
        providers.append('gemini')
    return providers

def print_config_status():
    """Print configuration status."""
    print("=== API Key Configuration Status ===")
    print(f"OPENAI: {'✓ Configured' if is_configured('openai') else '✗ Not configured'}")
    print(f"GEMINI: {'✓ Configured' if is_configured('gemini') else '✗ Not configured'}")
    print("=====================================")

# Example usage
if __name__ == "__main__":
    print_config_status()
