"""Configuration constants for QR code generation.

This module centralizes all configuration values used across the application.
"""

from pathlib import Path

# Directory paths
OUTPUT_DIR = Path("generatedQRs")
CLI_OUTPUT_DIR = Path("sources")
DEFAULT_LOGO_PATH = Path("sources") / "Prysmian_Logo_CMYK_Black.png"

# Output settings
OUTPUT_DPI = 300
CM_TO_PX = OUTPUT_DPI / 2.54  # ~118.11 pixels per cm
IN_TO_PX = OUTPUT_DPI  # 300 pixels per inch

# Default dimensions (4"x2" at 300 DPI)
DEFAULT_WIDTH_INCHES = 4.0
DEFAULT_HEIGHT_INCHES = 2.0
BASELINE_WIDTH = 1200  # 4" * 300 DPI
BASELINE_HEIGHT = 600  # 2" * 300 DPI

# Design defaults
DEFAULT_LOGO_WIDTH = 400  # pixels at baseline
DEFAULT_QR_BOX_SIZE = 10
DEFAULT_TEXT_SIZE = 35  # points
DEFAULT_FONT = "Arial"
DEFAULT_LOGO_ALIGN = "left"
DEFAULT_QR_ALIGN = "center"
DEFAULT_TEXT_ALIGN = "center"

# Font mappings
FONT_FILE_MAP = {
    "Arial": "arial.ttf",
    "Times New Roman": "times.ttf",
    "Verdana": "verdana.ttf",
}

# Limits
MAX_BATCH_SIZE = 2000
MIN_LOGO_WIDTH = 50
MAX_LOGO_WIDTH = 1000
MIN_TEXT_SIZE = 6
MAX_TEXT_SIZE = 100

# QR Code settings
QR_ERROR_CORRECTION = "M"  # L, M, Q, H
QR_BORDER_SIZE = 4
