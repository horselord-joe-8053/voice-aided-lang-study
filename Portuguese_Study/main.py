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
from src.post_processing.output_manager import create_run_folder, save_text
from src.post_processing.audio_converter import convert_all_wavs_in_folder
from src.post_processing.text_renderer import create_text_screenshot
from src.post_processing.video_generator import generate_videos_for_run
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
    
    # Create output folder for this run
    print("Creating output folder...")
    output_folder = create_run_folder()
    print()
    
    # Generate and display paragraph
    paragraph = generate_and_display_paragraph()
    print()
    
    # Save text to file
    print("Saving text...")
    text_file = save_text(output_folder, paragraph)
    print()
    
    # Create TTS audio for configured providers
    if 'openai' in configured_providers:
        print("Creating OpenAI TTS audio...")
        tts_openai(paragraph, output_folder=output_folder)
        print()
    
    if 'gemini' in configured_providers:
        print("Creating Gemini TTS audio...")
        tts_gemini(paragraph, output_folder=output_folder)
        print()
    
    # Post-processing: Convert WAV to MP3
    print("Converting audio files to MP3...")
    mp3_files = convert_all_wavs_in_folder(output_folder)
    print(f"Created {len(mp3_files)} MP3 files")
    print()
    
    # Post-processing: Render text to image
    print("Rendering text as image...")
    text_image = create_text_screenshot(text_file)
    print()
    
    # Post-processing: Generate videos
    print("Generating videos...")
    video_files = generate_videos_for_run(output_folder, text_image)
    print(f"Created {len(video_files)} video files")
    print()
    
    # Print summary
    print("="*50)
    print("📁 Output Summary")
    print("="*50)
    print(f"Output folder: {output_folder}")
    print(f"Text file: {text_file}")
    print(f"Audio files (WAV): {len(configured_providers)}")
    print(f"Audio files (MP3): {len(mp3_files)}")
    print(f"Video files (MP4): {len(video_files)}")
    print("="*50)
    print()
    
    # Print cost report
    cost_tracker.print_daily_report()

if __name__ == "__main__":
    main()