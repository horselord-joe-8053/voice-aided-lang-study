"""
Pricing Configuration for TTS Providers

Contains current pricing information for different providers and models.
Prices are in USD per token (for input/output) or per request.
"""

from typing import Dict, Any
from datetime import datetime

class PricingConfig:
    """
    Manages pricing configuration for different TTS providers.
    """
    
    def __init__(self):
        self.pricing_data = {
            "openai": {
                "gpt-4o-mini-tts": {
                    "input_tokens_per_dollar": 1000000,  # $1 per 1M tokens
                    "output_tokens_per_dollar": 0,       # TTS doesn't have output tokens
                    "base_request_cost": 0.0,            # No base cost
                    "last_updated": "2024-01-15"
                }
            },
            "gemini": {
                "gemini-2.5-flash-preview-tts": {
                    "input_tokens_per_dollar": 2000000,  # $1 per 2M tokens (estimated)
                    "output_tokens_per_dollar": 0,       # TTS doesn't have output tokens
                    "base_request_cost": 0.0,            # No base cost
                    "last_updated": "2024-01-15"
                }
            }
        }
    
    def get_input_cost_per_token(self, provider: str, model: str) -> float:
        """
        Get the cost per input token for a specific provider and model.
        
        Args:
            provider: The TTS provider (e.g., 'openai', 'gemini')
            model: The model name (e.g., 'gpt-4o-mini-tts')
        
        Returns:
            float: Cost per input token in USD
        """
        try:
            tokens_per_dollar = self.pricing_data[provider][model]["input_tokens_per_dollar"]
            return 1.0 / tokens_per_dollar if tokens_per_dollar > 0 else 0.0
        except KeyError:
            print(f"Warning: No pricing data found for {provider}/{model}")
            return 0.0
    
    def get_output_cost_per_token(self, provider: str, model: str) -> float:
        """
        Get the cost per output token for a specific provider and model.
        
        Args:
            provider: The TTS provider (e.g., 'openai', 'gemini')
            model: The model name (e.g., 'gpt-4o-mini-tts')
        
        Returns:
            float: Cost per output token in USD
        """
        try:
            tokens_per_dollar = self.pricing_data[provider][model]["output_tokens_per_dollar"]
            return 1.0 / tokens_per_dollar if tokens_per_dollar > 0 else 0.0
        except KeyError:
            return 0.0
    
    def get_base_request_cost(self, provider: str, model: str) -> float:
        """
        Get the base cost per request for a specific provider and model.
        
        Args:
            provider: The TTS provider (e.g., 'openai', 'gemini')
            model: The model name (e.g., 'gpt-4o-mini-tts')
        
        Returns:
            float: Base cost per request in USD
        """
        try:
            return self.pricing_data[provider][model]["base_request_cost"]
        except KeyError:
            return 0.0
    
    def calculate_total_cost(self, provider: str, model: str, 
                           input_tokens: int, output_tokens: int = 0) -> float:
        """
        Calculate total cost for a request.
        
        Args:
            provider: The TTS provider
            model: The model name
            input_tokens: Number of input tokens
            output_tokens: Number of output tokens (default: 0)
        
        Returns:
            float: Total cost in USD
        """
        input_cost = self.get_input_cost_per_token(provider, model) * input_tokens
        output_cost = self.get_output_cost_per_token(provider, model) * output_tokens
        base_cost = self.get_base_request_cost(provider, model)
        
        return input_cost + output_cost + base_cost
    
    def update_pricing(self, provider: str, model: str, pricing_info: Dict[str, Any]):
        """
        Update pricing information for a specific provider and model.
        
        Args:
            provider: The TTS provider
            model: The model name
            pricing_info: Dictionary containing pricing information
        """
        if provider not in self.pricing_data:
            self.pricing_data[provider] = {}
        
        pricing_info["last_updated"] = datetime.now().isoformat()
        self.pricing_data[provider][model] = pricing_info
    
    def get_all_providers(self) -> list:
        """Get list of all configured providers."""
        return list(self.pricing_data.keys())
    
    def get_models_for_provider(self, provider: str) -> list:
        """Get list of all models for a specific provider."""
        return list(self.pricing_data.get(provider, {}).keys())
