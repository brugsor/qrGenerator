"""Windows clipboard operations.

This module provides Windows-specific clipboard functionality using win32clipboard.
"""

import io

import win32clipboard
from PIL import Image


def copy_image_to_clipboard(image: Image.Image) -> None:
    """Copy PIL Image to Windows clipboard as BMP.

    Args:
        image: PIL Image to copy

    Raises:
        Exception: If clipboard operation fails

    Note:
        This function is Windows-only and requires pywin32.
    """
    # Convert to RGB and save as BMP
    output = io.BytesIO()
    rgb_image = image.convert("RGB")
    rgb_image.save(output, format="BMP")

    # Remove BMP file header (first 14 bytes) for clipboard
    bmp_data = output.getvalue()[14:]

    # Copy to clipboard
    win32clipboard.OpenClipboard()
    try:
        win32clipboard.EmptyClipboard()
        win32clipboard.SetClipboardData(win32clipboard.CF_DIB, bmp_data)
    finally:
        win32clipboard.CloseClipboard()
