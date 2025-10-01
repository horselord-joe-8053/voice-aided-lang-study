import os
import requests
import base64
import struct
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
# WAV HEADER UTILITY
# -------------------------------
def add_wav_headers(raw_audio_data, sample_rate=24000, channels=1, bits_per_sample=16):
    """
    Add WAV file headers to raw PCM audio data.
    
    Args:
        raw_audio_data: Raw PCM audio data (bytes)
        sample_rate: Sample rate in Hz (default: 24000)
        channels: Number of audio channels (default: 1 for mono)
        bits_per_sample: Bits per sample (default: 16)
    
    Returns:
        bytes: Complete WAV file with headers
    """
    # Calculate sizes
    bytes_per_sample = bits_per_sample // 8
    block_align = channels * bytes_per_sample
    byte_rate = sample_rate * block_align
    data_size = len(raw_audio_data)
    file_size = 36 + data_size
    
    # Create WAV header
    wav_header = struct.pack('<4sI4s4sIHHIIHH4sI',
        b'RIFF',                    # Chunk ID
        file_size,                  # Chunk Size
        b'WAVE',                    # Format
        b'fmt ',                    # Subchunk1 ID
        16,                         # Subchunk1 Size
        1,                          # Audio Format (PCM)
        channels,                   # Number of Channels
        sample_rate,                # Sample Rate
        byte_rate,                  # Byte Rate
        block_align,                # Block Align
        bits_per_sample,            # Bits Per Sample
        b'data',                    # Subchunk2 ID
        data_size                   # Subchunk2 Size
    )
    
    return wav_header + raw_audio_data

# -------------------------------
# CONFIGURATION
# -------------------------------
# Gemini API key
# Get Gemini API key from configuration
GEMINI_API_KEY = get_api_key('gemini')

# Initialize cost tracker
cost_tracker = CostTracker()

# -------------------------------
# GEMINI TTS
# -------------------------------
def tts_gemini(text, filename=None, output_folder=None):
    """
    Convert text to speech using Gemini 2.5 Flash Preview TTS API
    Saves to WAV file with cost tracking and automatic filename generation.
    
    Args:
        text: Text to convert to speech
        filename: Output filename for the audio (optional, will be auto-generated if not provided)
        output_folder: Custom output folder (optional, uses default if not provided)
    
    Returns:
        str: Path to saved audio file, or None if failed
    """
    # Check if API key is configured
    if not is_configured('gemini'):
        print("Error: Gemini API key is not configured. Please set GEMINI_API_KEY environment variable or configure in config/api_key_config.py")
        return None
    
    # Start cost tracking
    request_id = cost_tracker.start_request("gemini", "gemini-2.5-flash-preview-tts", text)
    
    # Generate filename if not provided
    if filename is None:
        # If output_folder is provided, use simple filename, otherwise use auto-generated
        if output_folder:
            filename = "gemini.wav"
        else:
            filename = generate_audio_filename(request_id, "gemini")
    
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-tts:generateContent?key={GEMINI_API_KEY}"
    headers = {
        "Content-Type": "application/json"
    }
    
    # Gemini TTS request format
    payload = {
        "contents": [{
            "parts": [{
                "text": f"Generate speech for the following text in Brazilian Portuguese: {text}"
            }]
        }],
        "generationConfig": {
            "responseModalities": ["AUDIO"]
        }
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        
        if response.status_code == 200:
            result = response.json()
            
            # Check if audio data is in the response
            if 'candidates' in result and len(result['candidates']) > 0:
                candidate = result['candidates'][0]
                if 'content' in candidate and 'parts' in candidate['content']:
                    for part in candidate['content']['parts']:
                        if 'inlineData' in part:
                            mime_type = part['inlineData'].get('mimeType', '')
                            if 'audio/' in mime_type:
                                raw_audio_data = base64.b64decode(part['inlineData']['data'])
                                
                                # Add WAV headers to the raw audio data
                                audio_data = add_wav_headers(raw_audio_data, sample_rate=24000)
                                
                                audio_path = save_audio_file(audio_data, filename, output_folder)
                                
                                # Estimate audio duration (rough calculation: 1 second ≈ 16KB for typical TTS)
                                audio_duration = len(audio_data) / 16000 if len(audio_data) > 0 else 0
                                
                                # End cost tracking with success
                                cost_tracker.end_request(
                                    request_id=request_id,
                                    success=True,
                                    actual_input_tokens=None,  # Gemini TTS doesn't return token count
                                    audio_duration=audio_duration
                                )
                                
                                print(f"Saved Gemini TTS audio: {audio_path}")
                                return audio_path
            
            # End cost tracking with error (unexpected response format)
            cost_tracker.end_request(
                request_id=request_id,
                success=False,
                error="Unexpected response format"
            )
            
            print("Gemini TTS response format unexpected:", result)
            return None
        else:
            # End cost tracking with error (API error)
            cost_tracker.end_request(
                request_id=request_id,
                success=False,
                error=f"API error: {response.text}"
            )
            
            print("Gemini TTS failed:", response.text)
            return None
            
    except Exception as e:
        # End cost tracking with error (exception)
        cost_tracker.end_request(
            request_id=request_id,
            success=False,
            error=str(e)
        )
        
        print(f"Gemini TTS error: {e}")
        return None

# -------------------------------
# MAIN EXECUTION
# -------------------------------
def main():
    """
    Main function to generate paragraph and create Gemini TTS audio.
    """
    # Generate and display paragraph
    paragraph = generate_and_display_paragraph()
    
    # Create Gemini TTS
    print("Creating Gemini TTS audio...")
    tts_gemini(paragraph)

if __name__ == "__main__":
    main()
