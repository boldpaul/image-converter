"""Core image conversion logic."""

import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

# Import pillow-avif-plugin to register AVIF support
import pillow_avif  # noqa: F401
from PIL import Image

from .formats import is_supported_format, get_output_path

logger = logging.getLogger(__name__)


@dataclass
class ConversionResult:
    """Result of an image conversion operation."""
    
    input_path: Path
    output_path: Optional[Path]
    success: bool
    error_message: Optional[str] = None
    
    @property
    def filename(self) -> str:
        """Get the input filename."""
        return self.input_path.name


class ImageConverter:
    """Converts PNG/JPEG images to AVIF format."""
    
    # Default quality setting (0-100, higher = better quality, larger file)
    DEFAULT_QUALITY: int = 80
    
    # Quality bounds
    MIN_QUALITY: int = 0
    MAX_QUALITY: int = 100
    
    def __init__(self, quality: int = DEFAULT_QUALITY):
        """Initialize the converter.
        
        Args:
            quality: AVIF compression quality (0-100). Default is 80.
        """
        self.quality = self._validate_quality(quality)
    
    def _validate_quality(self, quality: int) -> int:
        """Validate and clamp quality to valid range.
        
        Args:
            quality: Requested quality value.
            
        Returns:
            Quality value clamped to valid range.
        """
        if quality < self.MIN_QUALITY:
            logger.warning(
                f"Quality {quality} below minimum, using {self.MIN_QUALITY}"
            )
            return self.MIN_QUALITY
        if quality > self.MAX_QUALITY:
            logger.warning(
                f"Quality {quality} above maximum, using {self.MAX_QUALITY}"
            )
            return self.MAX_QUALITY
        return quality
    
    def convert(
        self,
        input_path: Path,
        output_dir: Optional[Path] = None,
        overwrite: bool = False,
    ) -> ConversionResult:
        """Convert a single image to AVIF format.
        
        Args:
            input_path: Path to the input image (PNG or JPEG).
            output_dir: Optional output directory. If None, saves alongside input.
            overwrite: Whether to overwrite existing output files.
            
        Returns:
            ConversionResult with success status and any error details.
        """
        input_path = Path(input_path)
        
        # Validate input file exists
        if not input_path.exists():
            return ConversionResult(
                input_path=input_path,
                output_path=None,
                success=False,
                error_message=f"File not found: {input_path}",
            )
        
        # Validate input format
        if not is_supported_format(input_path):
            return ConversionResult(
                input_path=input_path,
                output_path=None,
                success=False,
                error_message=f"Unsupported format: {input_path.suffix}",
            )
        
        # Determine output path
        output_path = get_output_path(input_path, output_dir)
        
        # Check if output exists and we shouldn't overwrite
        if output_path.exists() and not overwrite:
            return ConversionResult(
                input_path=input_path,
                output_path=output_path,
                success=False,
                error_message=f"Output exists (use --overwrite): {output_path}",
            )
        
        # Ensure output directory exists
        if output_dir is not None:
            output_dir.mkdir(parents=True, exist_ok=True)
        
        # Perform the conversion
        try:
            self._convert_image(input_path, output_path)
            return ConversionResult(
                input_path=input_path,
                output_path=output_path,
                success=True,
            )
        except Exception as e:
            logger.exception(f"Failed to convert {input_path}")
            return ConversionResult(
                input_path=input_path,
                output_path=output_path,
                success=False,
                error_message=str(e),
            )
    
    def _convert_image(self, input_path: Path, output_path: Path) -> None:
        """Perform the actual image conversion.
        
        Args:
            input_path: Path to input image.
            output_path: Path for output AVIF file.
            
        Raises:
            Exception: If conversion fails.
        """
        with Image.open(input_path) as img:
            # Preserve ICC profile if present
            icc_profile = img.info.get("icc_profile")
            
            # Handle transparency for PNG images
            # AVIF supports transparency, so we preserve RGBA mode
            if img.mode == "RGBA":
                # Keep RGBA for transparency support
                output_img = img
            elif img.mode == "P" and "transparency" in img.info:
                # Palette mode with transparency -> convert to RGBA
                output_img = img.convert("RGBA")
            elif img.mode in ("L", "LA"):
                # Grayscale images
                if img.mode == "LA":
                    output_img = img.convert("RGBA")
                else:
                    output_img = img.convert("RGB")
            else:
                # Convert to RGB for JPEG and other formats
                output_img = img.convert("RGB") if img.mode != "RGB" else img
            
            # Save as AVIF with quality setting
            save_kwargs = {
                "quality": self.quality,
            }
            
            # Preserve ICC profile if available
            if icc_profile:
                save_kwargs["icc_profile"] = icc_profile
            
            output_img.save(output_path, "AVIF", **save_kwargs)
            
            logger.debug(
                f"Converted {input_path.name} -> {output_path.name} "
                f"(quality={self.quality})"
            )

