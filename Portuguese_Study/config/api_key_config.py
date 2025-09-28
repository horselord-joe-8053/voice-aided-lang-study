"""
API Key Configuration for Portuguese Study TTS System

This module provides secure API key management for the TTS providers.
It supports both environment variables and direct configuration.

Usage:
    from config.api_key_config import get_api_key
    
    openai_key = get_api_key('openai')
    gemini_key = get_api_key('gemini')
"""

import os
from typing import Optional


class APIKeyConfig:
    """Manages API keys for TTS providers with fallback options."""
    
    def __init__(self):
        """Initialize the API key configuration."""
        # Direct API key configuration (for development/testing)
        # Replace these with your actual API keys or leave as None to use environment variables
        self._api_keys = {
            'openai': None,  # Set your OpenAI API key here or use OPENAI_API_KEY env var
            'gemini': None,  # Set your Gemini API key here or use GEMINI_API_KEY env var
        }
        
        # Environment variable mapping
        self._env_vars = {
            'openai': 'OPENAI_API_KEY',
            'gemini': 'GEMINI_API_KEY',
        }
    
    def get_api_key(self, provider: str) -> Optional[str]:
        """
        Get API key for a specific provider.
        
        Args:
            provider (str): The provider name ('openai' or 'gemini')
            
        Returns:
            Optional[str]: The API key if found, None otherwise
            
        Raises:
            ValueError: If provider is not supported
        """
        if provider not in self._api_keys:
            raise ValueError(f"Unsupported provider: {provider}. Supported providers: {list(self._api_keys.keys())}")
        
        # First, try direct configuration
        if self._api_keys[provider] is not None:
            return self._api_keys[provider]
        
        # Then, try environment variable
        env_var = self._env_vars[provider]
        return os.getenv(env_var)
    
    def set_api_key(self, provider: str, api_key: str) -> None:
        """
        Set API key for a specific provider.
        
        Args:
            provider (str): The provider name ('openai' or 'gemini')
            api_key (str): The API key to set
            
        Raises:
            ValueError: If provider is not supported
        """
        if provider not in self._api_keys:
            raise ValueError(f"Unsupported provider: {provider}. Supported providers: {list(self._api_keys.keys())}")
        
        self._api_keys[provider] = api_key
    
    def is_configured(self, provider: str) -> bool:
        """
        Check if API key is configured for a provider.
        
        Args:
            provider (str): The provider name
            
        Returns:
            bool: True if API key is available, False otherwise
        """
        return self.get_api_key(provider) is not None
    
    def get_configured_providers(self) -> list:
        """
        Get list of providers with configured API keys.
        
        Returns:
            list: List of provider names that have API keys configured
        """
        return [provider for provider in self._api_keys.keys() if self.is_configured(provider)]
    
    def print_config_status(self) -> None:
        """Print the configuration status for all providers."""
        print("=== API Key Configuration Status ===")
        for provider in self._api_keys.keys():
            status = "✓ Configured" if self.is_configured(provider) else "✗ Not configured"
            print(f"{provider.upper()}: {status}")
        print("=====================================")


# Global instance
_api_config = APIKeyConfig()


def get_api_key(provider: str) -> Optional[str]:
    """
    Convenience function to get API key for a provider.
    
    Args:
        provider (str): The provider name ('openai' or 'gemini')
        
    Returns:
        Optional[str]: The API key if found, None otherwise
    """
    return _api_config.get_api_key(provider)


def set_api_key(provider: str, api_key: str) -> None:
    """
    Convenience function to set API key for a provider.
    
    Args:
        provider (str): The provider name ('openai' or 'gemini')
        api_key (str): The API key to set
    """
    _api_config.set_api_key(provider, api_key)


def is_configured(provider: str) -> bool:
    """
    Convenience function to check if API key is configured.
    
    Args:
        provider (str): The provider name
        
    Returns:
        bool: True if API key is available, False otherwise
    """
    return _api_config.is_configured(provider)


def get_configured_providers() -> list:
    """
    Convenience function to get list of configured providers.
    
    Returns:
        list: List of provider names that have API keys configured
    """
    return _api_config.get_configured_providers()


def print_config_status() -> None:
    """Convenience function to print configuration status."""
    _api_config.print_config_status()


# Example usage and configuration
if __name__ == "__main__":
    # Example: Set API keys directly (for development)
    # set_api_key('openai', 'your-openai-api-key-here')
    # set_api_key('gemini', 'your-gemini-api-key-here')
    
    # Print current configuration status
    print_config_status()
    
    # Example: Check if providers are configured
    if is_configured('openai'):
        print("OpenAI is configured and ready to use")
    else:
        print("OpenAI is not configured. Please set OPENAI_API_KEY environment variable or configure directly.")
    
    if is_configured('gemini'):
        print("Gemini is configured and ready to use")
    else:
        print("Gemini is not configured. Please set GEMINI_API_KEY environment variable or configure directly.")
