"""
Audio Utilities Module

This module provides common audio-related utilities for the TTS system.
"""

import os
from datetime import datetime

# -------------------------------
# CONFIGURATION
# -------------------------------
# Output folder
OUTPUT_FOLDER = "audio_outputs"
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# -------------------------------
# FILENAME GENERATION
# -------------------------------
def generate_audio_filename(request_id: str, provider: str) -> str:
    """
    Generate audio filename in the format: output_YYmmdd_seqNum_provider.wav
    
    Args:
        request_id: Request ID in format "request_XXX_provider"
        provider: TTS provider name (e.g., "openai", "gemini")
    
    Returns:
        str: Generated filename
    """
    # Extract sequence number from request_id
    try:
        seq_num = request_id.split("_")[1]
    except (IndexError, ValueError):
        seq_num = "001"  # Default fallback
    
    # Get current date in YYmmdd format
    date_str = datetime.now().strftime("%y%m%d")
    
    # Generate filename
    filename = f"output_{date_str}_{seq_num}_{provider}.wav"
    return filename

# -------------------------------
# AUDIO SAVING UTILITY
# -------------------------------
def save_audio_file(audio_data, filename):
    """
    Save audio data to file in the output folder.
    
    Args:
        audio_data: Raw audio data (bytes)
        filename: Name of the output file
    
    Returns:
        str: Path to the saved audio file
    """
    audio_path = os.path.join(OUTPUT_FOLDER, filename)
    with open(audio_path, "wb") as f:
        f.write(audio_data)
    return audio_path
