"""Entry point for running the package as a module.

Usage:
    python -m image_converter [arguments]
"""

import sys

from .cli.app import main

if __name__ == "__main__":
    sys.exit(main())

