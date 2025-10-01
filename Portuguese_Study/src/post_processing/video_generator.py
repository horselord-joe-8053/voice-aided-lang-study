"""
Video Generator Module

Creates MP4 videos by combining static images with audio files using ffmpeg.
"""

import os
import subprocess


def create_video_from_audio_and_image(audio_path, image_path, output_path, 
                                     video_codec='libx264', audio_codec='aac', 
                                     audio_bitrate='192k'):
    """
    Create an MP4 video from an audio file and a static image.
    
    Args:
        audio_path: Path to the audio file (WAV or MP3)
        image_path: Path to the static image (PNG or JPG)
        output_path: Path to save the output MP4 video
        video_codec: Video codec to use (default: 'libx264')
        audio_codec: Audio codec to use (default: 'aac')
        audio_bitrate: Audio bitrate (default: '192k')
    
    Returns:
        str: Path to the created video file
    
    Raises:
        FileNotFoundError: If audio or image files don't exist
        RuntimeError: If ffmpeg conversion fails
    """
    if not os.path.exists(audio_path):
        raise FileNotFoundError(f"Audio file not found: {audio_path}")
    
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"Image file not found: {image_path}")
    
    # Build ffmpeg command
    # -loop 1: Loop the image
    # -i image.png: Input image
    # -i audio.wav: Input audio
    # -c:v libx264: Video codec
    # -tune stillimage: Optimize for static image
    # -c:a aac: Audio codec
    # -b:a 192k: Audio bitrate
    # -pix_fmt yuv420p: Pixel format for compatibility
    # -shortest: End video when audio ends
    ffmpeg_cmd = [
        'ffmpeg',
        '-y',  # Overwrite output file if it exists
        '-loop', '1',  # Loop the image
        '-i', image_path,  # Input image
        '-i', audio_path,  # Input audio
        '-c:v', video_codec,  # Video codec
        '-tune', 'stillimage',  # Optimize for static image
        '-c:a', audio_codec,  # Audio codec
        '-b:a', audio_bitrate,  # Audio bitrate
        '-pix_fmt', 'yuv420p',  # Pixel format for compatibility
        '-shortest',  # End when audio ends
        output_path
    ]
    
    try:
        # Run ffmpeg command
        result = subprocess.run(
            ffmpeg_cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True
        )
        
        print(f"Created video: {output_path}")
        return output_path
    
    except subprocess.CalledProcessError as e:
        error_msg = e.stderr.decode('utf-8') if e.stderr else str(e)
        raise RuntimeError(f"ffmpeg failed to create video: {error_msg}")
    
    except FileNotFoundError:
        raise RuntimeError(
            "ffmpeg not found. Please install ffmpeg:\n"
            "  macOS: brew install ffmpeg\n"
            "  Ubuntu/Debian: sudo apt-get install ffmpeg\n"
            "  Windows: choco install ffmpeg"
        )


def generate_videos_for_run(folder_path, text_image_path):
    """
    Generate MP4 videos for all audio files in the run folder.
    
    Args:
        folder_path: Path to the output folder containing audio files
        text_image_path: Path to the text screenshot image
    
    Returns:
        dict: Mapping of provider name to MP4 file path
    """
    results = {}
    
    # Look for gemini.wav and openai.wav
    for provider in ['gemini', 'openai']:
        audio_file = os.path.join(folder_path, f"{provider}.wav")
        
        if os.path.exists(audio_file):
            try:
                video_file = os.path.join(folder_path, f"{provider}.mp4")
                create_video_from_audio_and_image(
                    audio_file, 
                    text_image_path, 
                    video_file
                )
                results[provider] = video_file
            except Exception as e:
                print(f"Warning: Failed to create video for {provider}: {str(e)}")
                continue
    
    return results

