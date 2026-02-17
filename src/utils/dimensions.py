"""Dimension conversion utilities.

This module provides functions for converting between different units of measurement.
"""

from typing import Literal

from ..config import CM_TO_PX, IN_TO_PX

UnitType = Literal["cm", "in", "px"]


def convert_to_pixels(
    width: float, height: float, unit: UnitType
) -> tuple[int, int]:
    """Convert dimensions from given unit to pixels.

    Args:
        width: Width value in the specified unit
        height: Height value in the specified unit
        unit: Unit of measurement ("cm", "in", or "px")

    Returns:
        Tuple of (width_pixels, height_pixels)

    Raises:
        ValueError: If dimensions are not positive or unit is invalid
    """
    if width <= 0 or height <= 0:
        raise ValueError("Width and height must be positive values")

    if unit == "cm":
        width_px = max(1, int(width * CM_TO_PX))
        height_px = max(1, int(height * CM_TO_PX))
    elif unit == "in":
        width_px = max(1, int(width * IN_TO_PX))
        height_px = max(1, int(height * IN_TO_PX))
    elif unit == "px":
        width_px = max(1, int(width))
        height_px = max(1, int(height))
    else:
        raise ValueError(f"Invalid unit: {unit}. Must be 'cm', 'in', or 'px'")

    return width_px, height_px
