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

# -------------------------------
# MAIN EXECUTION
# -------------------------------
def main():
    """
    Main function to generate paragraph and create audio using both TTS providers.
    """
    # Initialize cost tracker for reporting
    cost_tracker = CostTracker()
    
    # Generate and display paragraph
    paragraph = generate_and_display_paragraph()
    
    # Create OpenAI TTS
    print("Creating OpenAI TTS audio...")
    tts_openai(paragraph)
    print()
    
    # Create Gemini TTS
    print("Creating Gemini TTS audio...")
    tts_gemini(paragraph)
    print()
    
    # Print cost report
    cost_tracker.print_daily_report()

if __name__ == "__main__":
    main()