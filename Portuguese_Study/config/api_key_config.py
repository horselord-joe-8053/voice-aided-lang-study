"""
Simple API Key Configuration for Portuguese Study TTS System

Just set your API keys as constants below, or use environment variables.
"""

import os

# ===========================================
# API KEY CONFIGURATION
# ===========================================
# Set your API keys here, or leave as None to use environment variables

OPENAI_API_KEY = None  # Set your OpenAI API key here, or use OPENAI_API_KEY env var
GEMINI_API_KEY = None  # Set your Gemini API key here, or use GEMINI_API_KEY env var

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
