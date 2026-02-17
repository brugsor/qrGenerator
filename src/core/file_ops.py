"""File operations for QR code export and batch processing.

This module handles all file I/O operations including saving individual
QR codes and batch exporting to ZIP archives.
"""

import io
import zipfile
from pathlib import Path
from typing import Callable

from PIL import Image

from ..config import OUTPUT_DPI


def save_qr_image(
    image: Image.Image, filepath: Path, dpi: int = OUTPUT_DPI
) -> None:
    """Save QR code image to file with metadata.

    Args:
        image: PIL Image to save
        filepath: Destination file path
        dpi: DPI metadata for the image

    Raises:
        OSError: If file cannot be written
    """
    filepath = Path(filepath)
    filepath.parent.mkdir(parents=True, exist_ok=True)
    image.save(filepath, dpi=(dpi, dpi))


def export_qr_codes_to_zip(
    texts: list[str],
    zip_path: Path,
    image_builder: Callable[[str], Image.Image],
    progress_callback: Callable[[int], None] | None = None,
    cancel_flag: Callable[[], bool] | None = None,
) -> bool:
    """Export multiple QR codes to a ZIP archive.

    Args:
        texts: List of text strings to encode
        zip_path: Path for output ZIP file
        image_builder: Callable that takes text and returns a PIL Image
        progress_callback: Optional callback function called with current count
        cancel_flag: Optional callable that returns True if export should be cancelled

    Returns:
        True if export completed successfully, False if cancelled

    Raises:
        OSError: If ZIP file cannot be created
        Exception: If image generation fails
    """
    zip_path = Path(zip_path)
    zip_path.parent.mkdir(parents=True, exist_ok=True)

    total = len(texts)
    completed = 0

    try:
        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
            for i, text in enumerate(texts):
                # Check for cancellation
                if cancel_flag and cancel_flag():
                    return False

                # Generate QR code image
                img = image_builder(text)

                # Save to buffer
                buf = io.BytesIO()
                img.save(buf, format="PNG", dpi=(OUTPUT_DPI, OUTPUT_DPI))

                # Add to ZIP
                entry_name = f"qr_{i + 1:04d}.png"
                zf.writestr(entry_name, buf.getvalue())

                completed += 1

                # Report progress
                if progress_callback:
                    progress_callback(completed)

        return True

    except Exception as e:
        # Clean up partial ZIP on error
        if zip_path.exists():
            try:
                zip_path.unlink()
            except OSError:
                pass
        raise e
