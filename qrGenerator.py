"""QR Code Generator - CLI Entry Point

Command-line interface for generating basic QR code images.
Outputs bare QR code PNGs to the sources/ directory.

This module serves as the CLI entry point. The core QR generation logic
has been refactored into the src/ package for better modularity.

Usage:
    python qrGenerator.py <string1> <string2> ...
"""

import sys
from pathlib import Path

import qrcode

from src.config import CLI_OUTPUT_DIR


def generate_qr_codes(strings: list[str]) -> None:
    """Generate QR code images from a list of strings.

    Args:
        strings: List of text strings to encode as QR codes

    Each QR code is saved as qr_1.png, qr_2.png, etc. in the sources/ directory.
    """
    CLI_OUTPUT_DIR.mkdir(exist_ok=True)

    for i, text in enumerate(strings):
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_M,
            box_size=10,
            border=4,
        )
        qr.add_data(text)
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")
        filename = f"qr_{i + 1}.png"
        filepath = CLI_OUTPUT_DIR / filename
        img.save(filepath)
        print(f"[{i + 1}/{len(strings)}] Saved: {filepath}  ->  {text!r}")


def main() -> None:
    """Parse command-line arguments and generate QR codes."""
    if len(sys.argv) < 2:
        print("Usage: python qrGenerator.py <string1> <string2> ...")
        sys.exit(1)

    generate_qr_codes(sys.argv[1:])


if __name__ == "__main__":
    main()
