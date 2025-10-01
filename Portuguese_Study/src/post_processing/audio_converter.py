"""
Audio Converter Module

Handles conversion of WAV files to MP3 format using pydub.
"""

import os
from pydub import AudioSegment


def wav_to_mp3(wav_path, mp3_path=None, bitrate='192k'):
    """
    Convert a WAV file to MP3 format.
    Note: If the file is already MP3, it will be copied instead of converted.
    
    Args:
        wav_path: Path to the input WAV file
        mp3_path: Path to the output MP3 file (if None, auto-generated)
        bitrate: MP3 bitrate (default: '192k')
    
    Returns:
        str: Path to the created MP3 file
    
    Raises:
        FileNotFoundError: If the WAV file doesn't exist
        RuntimeError: If conversion fails
    """
    if not os.path.exists(wav_path):
        raise FileNotFoundError(f"WAV file not found: {wav_path}")
    
    # Auto-generate MP3 path if not provided
    if mp3_path is None:
        mp3_path = wav_path.replace('.wav', '.mp3')
    
    try:
        # Try to load as WAV first
        try:
            audio = AudioSegment.from_wav(wav_path)
        except:
            # If WAV loading fails, try as MP3 (some TTS APIs return MP3 with .wav extension)
            try:
                audio = AudioSegment.from_mp3(wav_path)
            except:
                # Last resort: try to load as generic audio file
                audio = AudioSegment.from_file(wav_path)
        
        # Export as MP3
        audio.export(mp3_path, format='mp3', bitrate=bitrate)
        
        print(f"Converted WAV to MP3: {mp3_path}")
        return mp3_path
    
    except Exception as e:
        raise RuntimeError(f"Failed to convert {wav_path} to MP3: {str(e)}")


def convert_all_wavs_in_folder(folder_path, bitrate='192k'):
    """
    Convert all WAV files in a folder to MP3.
    
    Args:
        folder_path: Path to the folder containing WAV files
        bitrate: MP3 bitrate (default: '192k')
    
    Returns:
        dict: Mapping of provider name to MP3 file path
    """
    results = {}
    
    # Look for gemini.wav and openai.wav
    for provider in ['gemini', 'openai']:
        wav_file = os.path.join(folder_path, f"{provider}.wav")
        
        if os.path.exists(wav_file):
            try:
                mp3_file = wav_to_mp3(wav_file, bitrate=bitrate)
                results[provider] = mp3_file
            except Exception as e:
                print(f"Warning: Failed to convert {provider}.wav: {str(e)}")
                continue
    
    return results

