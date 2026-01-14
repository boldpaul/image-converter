"""Supported image formats and validation utilities."""

from pathlib import Path
from typing import Set

# Supported input formats (lowercase extensions)
SUPPORTED_INPUT_FORMATS: Set[str] = {".png", ".jpg", ".jpeg"}

# Output format
OUTPUT_FORMAT: str = ".avif"


def is_supported_format(file_path: Path) -> bool:
    """Check if a file has a supported input format.
    
    Args:
        file_path: Path to the image file.
        
    Returns:
        True if the file extension is supported, False otherwise.
    """
    return file_path.suffix.lower() in SUPPORTED_INPUT_FORMATS


def get_output_path(input_path: Path, output_dir: Path | None = None) -> Path:
    """Generate the output path for a converted file.
    
    Args:
        input_path: Path to the input image.
        output_dir: Optional output directory. If None, uses input file's directory.
        
    Returns:
        Path for the output AVIF file.
    """
    output_name = input_path.stem + OUTPUT_FORMAT
    
    if output_dir is not None:
        return output_dir / output_name
    
    return input_path.parent / output_name

