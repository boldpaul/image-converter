"""Setup script for the image-converter package."""

from pathlib import Path
from setuptools import setup, find_packages

# Read the README for long description
readme_path = Path(__file__).parent / "README.md"
long_description = readme_path.read_text(encoding="utf-8") if readme_path.exists() else ""

# Read version from package
version = {}
version_path = Path(__file__).parent / "src" / "image_converter" / "__init__.py"
exec(version_path.read_text(encoding="utf-8"), version)

setup(
    name="image-converter",
    version=version.get("__version__", "1.0.0"),
    author="Your Name",
    author_email="your.email@example.com",
    description="Convert PNG and JPEG images to AVIF format",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/image-converter",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    python_requires=">=3.10",
    install_requires=[
        "Pillow>=10.0.0",
        "pillow-avif-plugin>=1.4.0",
    ],
    entry_points={
        "console_scripts": [
            "image-converter=image_converter.cli.app:main",
            "img2avif=image_converter.cli.app:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Multimedia :: Graphics :: Graphics Conversion",
    ],
    keywords="image converter avif png jpeg jpg compression",
)

