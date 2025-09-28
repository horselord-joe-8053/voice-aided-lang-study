import os
import openai
try:
    from src.text_generation.input_text_gen import generate_and_display_paragraph
    from src.utils.audio_utils import save_audio_file, generate_audio_filename
    from cost_monitor.cost_tracker import CostTracker
    from config.api_key_config import get_api_key, is_configured
except ImportError:
    # For running this file directly
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
    from src.text_generation.input_text_gen import generate_and_display_paragraph
    from src.utils.audio_utils import save_audio_file, generate_audio_filename
    from cost_monitor.cost_tracker import CostTracker
    from config.api_key_config import get_api_key, is_configured

# -------------------------------
# CONFIGURATION
# -------------------------------
# Get OpenAI API key from configuration
OPENAI_API_KEY = get_api_key('openai')

# Initialize cost tracker
cost_tracker = CostTracker()

# -------------------------------
# OPENAI TTS
# -------------------------------
def tts_openai(text, filename=None):
    """
    Convert text to speech using OpenAI TTS (gpt-4o-mini-tts or similar)
    Saves to WAV file with cost tracking and automatic filename generation.
    
    Args:
        text: Text to convert to speech
        filename: Output filename for the audio (optional, will be auto-generated if not provided)
    
    Returns:
        str: Path to saved audio file, or None if failed
    """
    # Check if API key is configured
    if not is_configured('openai'):
        print("Error: OpenAI API key is not configured. Please set OPENAI_API_KEY environment variable or configure in config/api_key_config.py")
        return None
    
    # Start cost tracking
    request_id = cost_tracker.start_request("openai", "gpt-4o-mini-tts", text)
    
    # Generate filename if not provided
    if filename is None:
        filename = generate_audio_filename(request_id, "openai")
    
    openai.api_key = OPENAI_API_KEY

    try:
        response = openai.audio.speech.create(
            model="gpt-4o-mini-tts",
            voice="alloy",  # you can experiment with voices
            input=text
        )

        audio_data = response.read()
        audio_path = save_audio_file(audio_data, filename)
        
        # Estimate audio duration (rough calculation: 1 second ≈ 16KB for typical TTS)
        audio_duration = len(audio_data) / 16000 if len(audio_data) > 0 else 0
        
        # End cost tracking with success
        cost_tracker.end_request(
            request_id=request_id,
            success=True,
            actual_input_tokens=None,  # OpenAI TTS doesn't return token count
            audio_duration=audio_duration
        )
        
        print(f"Saved OpenAI TTS audio: {audio_path}")
        return audio_path
        
    except Exception as e:
        # End cost tracking with error
        cost_tracker.end_request(
            request_id=request_id,
            success=False,
            error=str(e)
        )
        
        print(f"OpenAI TTS error: {e}")
        return None

# -------------------------------
# MAIN EXECUTION
# -------------------------------
def main():
    """
    Main function to generate paragraph and create OpenAI TTS audio.
    """
    # Generate and display paragraph
    paragraph = generate_and_display_paragraph()
    
    # Create OpenAI TTS
    print("Creating OpenAI TTS audio...")
    tts_openai(paragraph)

if __name__ == "__main__":
    main()
