"""
Portuguese Numbers TTS Orchestrator

This script orchestrates both OpenAI and Gemini TTS providers to generate
audio exercises for Portuguese number learning.

The system is organized in a modular structure:
- src/text_generation/input_text_gen.py - Text generation logic
- src/tts_providers/txt_to_voice_openai.py - OpenAI TTS implementation
- src/tts_providers/txt_to_voice_gemini.py - Gemini TTS implementation
- src/utils/audio_utils.py - Common audio utilities
"""

from src.text_generation.input_text_gen import generate_and_display_paragraph
from src.tts_providers.txt_to_voice_openai import tts_openai
from src.tts_providers.txt_to_voice_gemini import tts_gemini
from cost_monitor.cost_tracker import CostTracker
from config.api_key_config import print_config_status, get_configured_providers

# -------------------------------
# MAIN EXECUTION
# -------------------------------
def main():
    """
    Main function to generate paragraph and create audio using both TTS providers.
    """
    # Check API key configuration
    print("=== Portuguese Study TTS System ===")
    print_config_status()
    
    configured_providers = get_configured_providers()
    if not configured_providers:
        print("\n❌ No API keys configured!")
        print("Please set your API keys using one of these methods:")
        print("1. Environment variables: OPENAI_API_KEY and GEMINI_API_KEY")
        print("2. Direct configuration in config/api_key_config.py")
        print("3. Copy config/api_keys_example.py to config/api_keys.py and add your keys")
        return
    
    print(f"\n✅ Configured providers: {', '.join(configured_providers)}")
    print()
    
    # Initialize cost tracker for reporting
    cost_tracker = CostTracker()
    
    # Generate and display paragraph
    paragraph = generate_and_display_paragraph()
    print()
    
    # Create TTS audio for configured providers
    if 'openai' in configured_providers:
        print("Creating OpenAI TTS audio...")
        tts_openai(paragraph)
        print()
    
    if 'gemini' in configured_providers:
        print("Creating Gemini TTS audio...")
        tts_gemini(paragraph)
        print()
    
    # Print cost report
    cost_tracker.print_daily_report()

if __name__ == "__main__":
    main()