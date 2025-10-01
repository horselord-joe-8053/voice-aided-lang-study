"""
Post-Processing Module

This module handles post-processing of TTS outputs including:
- Output folder management
- Audio format conversion (WAV to MP3)
- Text rendering to images
- Video generation (audio + static image)
"""

from .output_manager import create_run_folder, save_text
from .audio_converter import wav_to_mp3, convert_all_wavs_in_folder
from .text_renderer import render_text_to_image, create_text_screenshot
from .video_generator import create_video_from_audio_and_image, generate_videos_for_run

__all__ = [
    'create_run_folder',
    'save_text',
    'wav_to_mp3',
    'convert_all_wavs_in_folder',
    'render_text_to_image',
    'create_text_screenshot',
    'create_video_from_audio_and_image',
    'generate_videos_for_run',
]

