"""
Output Manager Module

Handles creation and management of output folders for each TTS run.
"""

import os
from pathlib import Path
from datetime import datetime
import glob


def get_next_sequence_number(base_dir, date_str):
    """
    Find the next available sequence number for a given date.
    
    Args:
        base_dir: Base directory to search in
        date_str: Date string in YYMMDD format
    
    Returns:
        int: Next available sequence number
    """
    pattern = os.path.join(base_dir, f"{date_str}_*_output")
    existing_folders = glob.glob(pattern)
    
    if not existing_folders:
        return 1
    
    # Extract sequence numbers from existing folders
    sequence_numbers = []
    for folder in existing_folders:
        folder_name = os.path.basename(folder)
        parts = folder_name.split('_')
        if len(parts) >= 2:
            try:
                seq_num = int(parts[1])
                sequence_numbers.append(seq_num)
            except ValueError:
                continue
    
    if not sequence_numbers:
        return 1
    
    return max(sequence_numbers) + 1


def create_run_folder(base_dir='outputs'):
    """
    Create a new output folder for this run.
    
    Format: YYMMDD_XXX_output where XXX is a 3-digit sequence number
    
    Args:
        base_dir: Base directory for outputs (default: 'outputs')
    
    Returns:
        str: Full path to the created folder
    """
    # Create base directory if it doesn't exist
    Path(base_dir).mkdir(parents=True, exist_ok=True)
    
    # Get current date in YYMMDD format
    date_str = datetime.now().strftime('%y%m%d')
    
    # Get next sequence number
    seq_num = get_next_sequence_number(base_dir, date_str)
    
    # Format folder name
    folder_name = f"{date_str}_{seq_num:03d}_output"
    folder_path = os.path.join(base_dir, folder_name)
    
    # Create the folder
    Path(folder_path).mkdir(parents=True, exist_ok=True)
    
    print(f"Created output folder: {folder_path}")
    return folder_path


def save_text(folder_path, text, filename='text.txt'):
    """
    Save generated text to a file in the output folder.
    
    Args:
        folder_path: Path to the output folder
        text: Text content to save
        filename: Name of the text file (default: 'text.txt')
    
    Returns:
        str: Full path to the saved text file
    """
    text_file_path = os.path.join(folder_path, filename)
    
    with open(text_file_path, 'w', encoding='utf-8') as f:
        f.write(text)
    
    print(f"Saved text to: {text_file_path}")
    return text_file_path


def get_audio_file_path(folder_path, provider, extension='wav'):
    """
    Get the path for an audio file in the output folder.
    
    Args:
        folder_path: Path to the output folder
        provider: Provider name ('openai' or 'gemini')
        extension: File extension (default: 'wav')
    
    Returns:
        str: Full path to the audio file
    """
    filename = f"{provider}.{extension}"
    return os.path.join(folder_path, filename)

