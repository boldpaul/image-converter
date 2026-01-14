"""Command-line interface for the image converter."""

import argparse
import sys
from pathlib import Path
from typing import List, Optional

from .. import __version__
from ..core.converter import ImageConverter
from ..core.formats import SUPPORTED_INPUT_FORMATS
from ..utils.batch import BatchProcessor
from ..utils.logger import setup_logger


def create_parser() -> argparse.ArgumentParser:
    """Create the argument parser for the CLI.
    
    Returns:
        Configured argument parser.
    """
    parser = argparse.ArgumentParser(
        prog="image-converter",
        description="Convert PNG and JPEG images to AVIF format.",
        epilog=(
            "Examples:\n"
            "  %(prog)s photo.png                    # Convert single file\n"
            "  %(prog)s photos/                      # Convert all images in folder\n"
            "  %(prog)s *.jpg -o converted/ -q 90   # Batch convert with options\n"
            "  %(prog)s images/ -p 8 --overwrite    # Parallel conversion\n"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    
    # Version
    parser.add_argument(
        "-V", "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )
    
    # Input paths (positional, required)
    parser.add_argument(
        "input",
        nargs="+",
        type=Path,
        help="Input image file(s) or directory/directories to convert.",
    )
    
    # Output options
    output_group = parser.add_argument_group("Output Options")
    output_group.add_argument(
        "-o", "--output",
        type=Path,
        default=None,
        metavar="DIR",
        help="Output directory for converted files. Default: same as input.",
    )
    output_group.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite existing output files.",
    )
    
    # Quality options
    quality_group = parser.add_argument_group("Quality Options")
    quality_group.add_argument(
        "-q", "--quality",
        type=int,
        default=80,
        metavar="N",
        help="AVIF quality (0-100). Higher = better quality, larger file. Default: 80.",
    )
    
    # Processing options
    proc_group = parser.add_argument_group("Processing Options")
    proc_group.add_argument(
        "-p", "--parallel",
        type=int,
        default=4,
        metavar="N",
        help="Number of parallel workers. Default: 4.",
    )
    proc_group.add_argument(
        "--no-recursive",
        action="store_true",
        help="Don't search directories recursively.",
    )
    
    # Logging options
    log_group = parser.add_argument_group("Logging Options")
    log_group.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable verbose (debug) output.",
    )
    log_group.add_argument(
        "--log-file",
        type=str,
        default=None,
        metavar="FILE",
        help="Write logs to file.",
    )
    log_group.add_argument(
        "--quiet",
        action="store_true",
        dest="quiet",
        help="Suppress progress output (only show summary).",
    )
    
    return parser


def print_summary(result, logger) -> None:
    """Print a summary of the batch conversion results.
    
    Args:
        result: BatchResult object.
        logger: Logger instance.
    """
    logger.info("")
    logger.info("=" * 50)
    logger.info("CONVERSION SUMMARY")
    logger.info("=" * 50)
    logger.info(f"  Total files:    {result.total}")
    logger.info(f"  Successful:     {result.successful}")
    logger.info(f"  Failed:         {result.failed}")
    logger.info(f"  Success rate:   {result.success_rate:.1f}%")
    logger.info("=" * 50)
    
    # List failed files if any
    if result.failed > 0:
        logger.info("")
        logger.warning("Failed conversions:")
        for conv_result in result.results:
            if not conv_result.success:
                logger.warning(f"  - {conv_result.filename}: {conv_result.error_message}")


def main(argv: Optional[List[str]] = None) -> int:
    """Main entry point for the CLI.
    
    Args:
        argv: Command-line arguments. If None, uses sys.argv.
        
    Returns:
        Exit code (0 for success, 1 for failure).
    """
    parser = create_parser()
    
    # Handle the conflict between -q for quality and -q for quiet
    # by checking raw args first
    if argv is None:
        argv = sys.argv[1:]
    
    # Parse arguments
    try:
        args = parser.parse_args(argv)
    except SystemExit as e:
        return e.code if e.code is not None else 1
    
    # Setup logging
    logger = setup_logger(
        verbose=args.verbose,
        log_file=args.log_file,
    )
    
    # Log startup info
    logger.info(f"Image Converter v{__version__}")
    logger.info(f"Quality: {args.quality} | Workers: {args.parallel}")
    
    # Create converter and processor
    converter = ImageConverter(quality=args.quality)
    processor = BatchProcessor(converter, max_workers=args.parallel)
    
    # Collect and process files
    files = processor.collect_files(
        args.input,
        recursive=not args.no_recursive,
    )
    
    if not files:
        logger.error("No supported image files found.")
        logger.info(f"Supported formats: {', '.join(sorted(SUPPORTED_INPUT_FORMATS))}")
        return 1
    
    logger.info(f"Found {len(files)} image(s) to convert")
    logger.info("")
    
    # Process files
    result = processor.process(
        files,
        output_dir=args.output,
        overwrite=args.overwrite,
        show_progress=not getattr(args, 'quiet', False),
    )
    
    # Print summary
    print_summary(result, logger)
    
    # Return appropriate exit code
    if result.failed > 0 and result.successful == 0:
        return 1  # Complete failure
    elif result.failed > 0:
        return 2  # Partial failure
    return 0  # Success


if __name__ == "__main__":
    sys.exit(main())

