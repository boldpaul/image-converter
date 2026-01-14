# Image Converter

A fast, parallel CLI tool to convert PNG and JPEG images to AVIF format.

# Project Structure

image-converter/
├── requirements.txt          # Dependencies (Pillow, pillow-avif-plugin)
├── pyproject.toml           # Modern Python packaging
├── setup.py                 # Backwards-compatible setup
├── README.md                # Documentation
└── src/image_converter/
    ├── __main__.py          # Entry point (python -m image_converter)
    ├── core/
    │   ├── converter.py     # Core conversion logic
    │   └── formats.py       # Format definitions
    ├── cli/
    │   └── app.py           # CLI with argparse
    └── utils/
        ├── batch.py         # ThreadPoolExecutor parallel processing
        └── logger.py        # Colored logging

## Features

- **Format Support**: Converts PNG and JPEG/JPG to AVIF
- **Transparency Preservation**: Maintains alpha channels from PNG images
- **Parallel Processing**: Multi-threaded batch conversion for speed
- **Quality Control**: Adjustable compression quality (0-100)
- **Cross-Platform**: Works on Windows, macOS, and Linux
- **Error Resilient**: Continues processing even if individual files fail
- **ICC Profile Support**: Preserves color profiles when available

## Installation

### From Source

```bash
# Clone or download the repository
cd image-converter

# Install with pip
pip install -e .

# Or install dependencies only
pip install -r requirements.txt
```

### Requirements

- Python 3.10+
- Pillow >= 10.0.0
- pillow-avif-plugin >= 1.4.0

## Usage

### Basic Usage

# Activate the virtual environment
```bash
source .venv/bin/activate
```
# Basic usage
```bash
image-converter photo.png                     # Single file
image-converter photos/                       # Entire folder
image-converter *.jpg -o output/ -q 90       # Custom output + quality
```
# Parallel processing (8 workers)
```bash
image-converter images/ -p 8 -q 85 --overwrite
```
# With logging
```bash
image-converter photos/ -v --log-file conversion.log

# Convert a single file
image-converter photo.png

# Convert all images in a folder
image-converter photos/

# Convert multiple files/folders
image-converter image1.png image2.jpg photos/
```

### Output Options

```bash
# Save to specific output directory
image-converter photos/ -o converted/

# Overwrite existing files
image-converter photos/ --overwrite
```

### Quality Settings

```bash
# Set quality (0-100, default: 80)
image-converter photos/ -q 90    # High quality, larger files
image-converter photos/ -q 60    # Lower quality, smaller files
```

### Parallel Processing

```bash
# Use 8 parallel workers (default: 4)
image-converter photos/ -p 8

# Single-threaded processing
image-converter photos/ -p 1
```

### Directory Options

```bash
# Don't search subdirectories
image-converter photos/ --no-recursive
```

### Logging Options

```bash
# Verbose output (debug info)
image-converter photos/ -v

# Save logs to file
image-converter photos/ --log-file conversion.log

# Quiet mode (summary only)
image-converter photos/ --quiet
```

### Running as Module

```bash
# Alternative invocation
python -m image_converter photos/ -q 85 -p 4
```

## Examples

### Convert a folder of photos

```bash
image-converter ~/Pictures/vacation/ -o ~/Pictures/vacation_avif/ -q 85 -p 8
```

### Batch convert with high quality

```bash
image-converter *.png *.jpg -o ./output/ -q 95 --overwrite
```

### Process large batch efficiently

```bash
image-converter /data/images/ -o /data/converted/ -p 16 -q 80 --log-file batch.log
```

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | All conversions successful |
| 1 | All conversions failed / No files found |
| 2 | Some conversions failed |

## Output

The tool provides colored terminal output showing:

- Progress for each file: `[1/10] ✓ photo.png`
- Errors inline: `[2/10] ✗ corrupt.png - Cannot identify image file`
- Summary with statistics at the end

## Supported Input Formats

- PNG (`.png`) - with transparency support
- JPEG (`.jpg`, `.jpeg`)

## Output Format

- AVIF (`.avif`) - modern, efficient image format with excellent compression

## License

MIT License
