"""
Text Renderer Module

Renders text content as images for use in video generation.
"""

import os
from PIL import Image, ImageDraw, ImageFont
import textwrap


def render_text_to_image(text, output_path, width=1920, height=1080, 
                        font_size=36, bg_color=(255, 255, 255), 
                        text_color=(0, 0, 0), padding=100):
    """
    Render text to an image with word wrapping.
    
    Args:
        text: Text content to render
        output_path: Path to save the output image
        width: Image width in pixels (default: 1920)
        height: Image height in pixels (default: 1080)
        font_size: Font size (default: 36)
        bg_color: Background color as RGB tuple (default: white)
        text_color: Text color as RGB tuple (default: black)
        padding: Padding around text in pixels (default: 100)
    
    Returns:
        str: Path to the created image file
    """
    # Create a new image with background color
    img = Image.new('RGB', (width, height), color=bg_color)
    draw = ImageDraw.Draw(img)
    
    # Try to use a system font, fallback to default if not available
    try:
        # Try common system fonts
        font = None
        font_paths = [
            "/System/Library/Fonts/Helvetica.ttc",  # macOS
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",  # Linux
            "C:\\Windows\\Fonts\\arial.ttf",  # Windows
        ]
        
        for font_path in font_paths:
            if os.path.exists(font_path):
                font = ImageFont.truetype(font_path, font_size)
                break
        
        if font is None:
            # Fallback to default font
            font = ImageFont.load_default()
    except Exception:
        # Use default font if all else fails
        font = ImageFont.load_default()
    
    # Calculate maximum width for text
    max_width = width - (2 * padding)
    
    # Word wrap the text
    wrapped_lines = []
    paragraphs = text.split('\n')
    
    for paragraph in paragraphs:
        # Estimate characters per line based on font size
        chars_per_line = max(10, max_width // (font_size // 2))
        lines = textwrap.wrap(paragraph, width=chars_per_line)
        wrapped_lines.extend(lines)
        if paragraph != paragraphs[-1]:
            wrapped_lines.append('')  # Add blank line between paragraphs
    
    # Calculate total text height
    line_height = font_size + 10
    total_text_height = len(wrapped_lines) * line_height
    
    # Start position (centered vertically)
    y_position = max(padding, (height - total_text_height) // 2)
    
    # Draw each line
    for line in wrapped_lines:
        # Get text bounding box to center horizontally
        bbox = draw.textbbox((0, 0), line, font=font)
        text_width = bbox[2] - bbox[0]
        
        # Center the text horizontally
        x_position = (width - text_width) // 2
        
        # Draw the text
        draw.text((x_position, y_position), line, fill=text_color, font=font)
        y_position += line_height
    
    # Save the image
    img.save(output_path, 'PNG')
    print(f"Rendered text to image: {output_path}")
    
    return output_path


def create_text_screenshot(text_file_path, output_image_path=None, **kwargs):
    """
    Create an image from a text file.
    
    Args:
        text_file_path: Path to the text file to render
        output_image_path: Path to save the output image (if None, auto-generated)
        **kwargs: Additional arguments to pass to render_text_to_image
    
    Returns:
        str: Path to the created image file
    """
    # Read the text file
    with open(text_file_path, 'r', encoding='utf-8') as f:
        text = f.read()
    
    # Auto-generate output path if not provided
    if output_image_path is None:
        base_dir = os.path.dirname(text_file_path)
        output_image_path = os.path.join(base_dir, 'text_image.png')
    
    # Render text to image
    return render_text_to_image(text, output_image_path, **kwargs)

