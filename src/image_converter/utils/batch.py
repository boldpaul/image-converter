"""Batch processing with parallel execution support."""

import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterator, List, Optional

from ..core.converter import ConversionResult, ImageConverter
from ..core.formats import SUPPORTED_INPUT_FORMATS

logger = logging.getLogger(__name__)


@dataclass
class BatchResult:
    """Summary of a batch conversion operation."""
    
    total: int = 0
    successful: int = 0
    failed: int = 0
    skipped: int = 0
    results: List[ConversionResult] = field(default_factory=list)
    
    @property
    def success_rate(self) -> float:
        """Calculate the success rate as a percentage."""
        if self.total == 0:
            return 0.0
        return (self.successful / self.total) * 100


class BatchProcessor:
    """Process multiple images in parallel."""
    
    DEFAULT_WORKERS: int = 4
    
    def __init__(
        self,
        converter: ImageConverter,
        max_workers: int = DEFAULT_WORKERS,
    ):
        """Initialize the batch processor.
        
        Args:
            converter: The ImageConverter instance to use.
            max_workers: Maximum number of parallel workers.
        """
        self.converter = converter
        self.max_workers = max(1, max_workers)
    
    def collect_files(self, paths: List[Path], recursive: bool = True) -> List[Path]:
        """Collect all supported image files from given paths.
        
        Args:
            paths: List of file or directory paths.
            recursive: Whether to search directories recursively.
            
        Returns:
            List of valid image file paths.
        """
        files: List[Path] = []
        
        for path in paths:
            path = Path(path)
            
            if path.is_file():
                if path.suffix.lower() in SUPPORTED_INPUT_FORMATS:
                    files.append(path)
                else:
                    logger.warning(f"Skipping unsupported file: {path}")
            
            elif path.is_dir():
                # Collect files from directory
                pattern = "**/*" if recursive else "*"
                for ext in SUPPORTED_INPUT_FORMATS:
                    files.extend(path.glob(f"{pattern}{ext}"))
                    # Also check uppercase extensions
                    files.extend(path.glob(f"{pattern}{ext.upper()}"))
            
            else:
                logger.warning(f"Path not found: {path}")
        
        # Remove duplicates while preserving order
        seen = set()
        unique_files = []
        for f in files:
            resolved = f.resolve()
            if resolved not in seen:
                seen.add(resolved)
                unique_files.append(f)
        
        return sorted(unique_files)
    
    def process(
        self,
        files: List[Path],
        output_dir: Optional[Path] = None,
        overwrite: bool = False,
        show_progress: bool = True,
    ) -> BatchResult:
        """Process a batch of image files.
        
        Args:
            files: List of image files to convert.
            output_dir: Optional output directory for all converted files.
            overwrite: Whether to overwrite existing files.
            show_progress: Whether to print progress updates.
            
        Returns:
            BatchResult with statistics and individual results.
        """
        result = BatchResult(total=len(files))
        
        if not files:
            logger.warning("No files to process")
            return result
        
        logger.info(f"Processing {len(files)} file(s) with {self.max_workers} worker(s)")
        
        # Process files in parallel
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all conversion tasks
            future_to_file = {
                executor.submit(
                    self.converter.convert,
                    file_path,
                    output_dir,
                    overwrite,
                ): file_path
                for file_path in files
            }
            
            # Collect results as they complete
            for i, future in enumerate(as_completed(future_to_file), 1):
                file_path = future_to_file[future]
                
                try:
                    conv_result = future.result()
                    result.results.append(conv_result)
                    
                    if conv_result.success:
                        result.successful += 1
                        status = "✓"
                        level = logging.INFO
                    else:
                        result.failed += 1
                        status = "✗"
                        level = logging.WARNING
                    
                    if show_progress:
                        msg = f"[{i}/{len(files)}] {status} {conv_result.filename}"
                        if conv_result.error_message:
                            msg += f" - {conv_result.error_message}"
                        logger.log(level, msg)
                        
                except Exception as e:
                    result.failed += 1
                    result.results.append(
                        ConversionResult(
                            input_path=file_path,
                            output_path=None,
                            success=False,
                            error_message=str(e),
                        )
                    )
                    if show_progress:
                        logger.error(f"[{i}/{len(files)}] ✗ {file_path.name} - {e}")
        
        return result
    
    def process_paths(
        self,
        paths: List[Path],
        output_dir: Optional[Path] = None,
        overwrite: bool = False,
        recursive: bool = True,
        show_progress: bool = True,
    ) -> BatchResult:
        """Collect files from paths and process them.
        
        Convenience method that combines collect_files and process.
        
        Args:
            paths: List of file or directory paths.
            output_dir: Optional output directory.
            overwrite: Whether to overwrite existing files.
            recursive: Whether to search directories recursively.
            show_progress: Whether to print progress updates.
            
        Returns:
            BatchResult with statistics and individual results.
        """
        files = self.collect_files(paths, recursive=recursive)
        return self.process(
            files,
            output_dir=output_dir,
            overwrite=overwrite,
            show_progress=show_progress,
        )

