"""QR code generation and image composition.

This module handles the core business logic of creating QR codes and
compositing them with logos and text into final images.
"""

import textwrap
from pathlib import Path
from typing import Literal

import qrcode
from PIL import Image, ImageDraw, ImageFont

from ..config import (
    BASELINE_HEIGHT,
    BASELINE_WIDTH,
    DEFAULT_FONT,
    DEFAULT_LOGO_ALIGN,
    DEFAULT_LOGO_WIDTH,
    DEFAULT_QR_ALIGN,
    DEFAULT_TEXT_ALIGN,
    DEFAULT_TEXT_SIZE,
    FONT_FILE_MAP,
    MAX_LOGO_WIDTH,
    MAX_TEXT_SIZE,
    MIN_LOGO_WIDTH,
    MIN_TEXT_SIZE,
    QR_BORDER_SIZE,
)

AlignmentType = Literal["left", "center", "right"]


class QRImageBuilder:
    """Builds QR code images with logo and text composition.

    This class encapsulates all logic for generating QR codes and compositing
    them with company logos and encoded text into print-ready images.
    """

    def __init__(
        self,
        logo_path: Path,
        logo_align: AlignmentType = DEFAULT_LOGO_ALIGN,
        qr_align: AlignmentType = DEFAULT_QR_ALIGN,
        text_align: AlignmentType = DEFAULT_TEXT_ALIGN,
        logo_width: int = DEFAULT_LOGO_WIDTH,
        qr_box_size: int = 10,
        text_size: int = DEFAULT_TEXT_SIZE,
        font_name: str = DEFAULT_FONT,
    ):
        """Initialize QR image builder with design settings.

        Args:
            logo_path: Path to the logo image file
            logo_align: Horizontal alignment for logo ("left", "center", "right")
            qr_align: Horizontal alignment for QR code
            text_align: Horizontal alignment for text
            logo_width: Target logo width in pixels (at baseline scale)
            qr_box_size: QR code box size parameter
            text_size: Text font size in points
            font_name: Font family name
        """
        self.logo_path = Path(logo_path)
        self.logo_align = logo_align
        self.qr_align = qr_align
        self.text_align = text_align
        self.logo_width = max(MIN_LOGO_WIDTH, min(MAX_LOGO_WIDTH, logo_width))
        self.qr_box_size = max(1, qr_box_size)
        self.text_size = max(MIN_TEXT_SIZE, min(MAX_TEXT_SIZE, text_size))
        self.font_name = font_name

    def build_image(self, text: str, target_width: int, target_height: int) -> Image.Image:
        """Build a QR code image at exact target dimensions.

        All elements (logo, QR, text, spacing) are sized proportionally to
        the target canvas. The QR code is always rendered as a perfect square.

        Args:
            text: Text to encode in the QR code
            target_width: Output image width in pixels
            target_height: Output image height in pixels

        Returns:
            PIL Image object containing the composed QR code image

        Raises:
            FileNotFoundError: If logo file does not exist
            ValueError: If target dimensions are invalid
        """
        if target_width <= 0 or target_height <= 0:
            raise ValueError("Target dimensions must be positive")

        if not self.logo_path.exists():
            raise FileNotFoundError(f"Logo file not found: {self.logo_path}")

        # Calculate proportional scale based on baseline dimensions
        scale = min(target_width / BASELINE_WIDTH, target_height / BASELINE_HEIGHT)

        # Calculate layout parameters
        padding = max(1, round(25 * scale))
        gap = max(1, round(15 * scale))
        content_width = target_width - 2 * padding

        # Load and scale logo
        logo = self._prepare_logo(content_width, scale)

        # Prepare text rendering
        font = self._get_font(scale)
        wrapped_text, text_width, text_height = self._prepare_text(
            text, font, content_width, scale
        )

        # Generate QR code (always square)
        qr_size = self._calculate_qr_size(
            target_height, padding, logo.height, gap, text_height
        )
        qr_image = self._generate_qr_code(text, qr_size)

        # Compose final image
        return self._compose_final_image(
            target_width,
            target_height,
            padding,
            gap,
            logo,
            qr_image,
            wrapped_text,
            text_width,
            font,
        )

    def _prepare_logo(self, content_width: int, scale: float) -> Image.Image:
        """Load and resize logo maintaining aspect ratio.

        Args:
            content_width: Maximum width for logo
            scale: Proportional scale factor

        Returns:
            Resized logo image with alpha channel
        """
        logo = Image.open(self.logo_path).convert("RGBA")
        logo_aspect = logo.width / logo.height

        # Scale logo width proportionally
        logo_width = max(1, round(self.logo_width * scale))
        if logo_width > content_width:
            logo_width = content_width

        logo_height = max(1, round(logo_width / logo_aspect))
        return logo.resize((logo_width, logo_height), Image.Resampling.LANCZOS)

    def _get_font(self, scale: float) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
        """Load font at scaled size.

        Args:
            scale: Proportional scale factor

        Returns:
            Font object for text rendering
        """
        scaled_text_size = max(6, round(self.text_size * scale))
        font_file = FONT_FILE_MAP.get(self.font_name, "arial.ttf")

        try:
            return ImageFont.truetype(font_file, scaled_text_size)
        except Exception:
            return ImageFont.load_default()

    def _prepare_text(
        self, text: str, font: ImageFont.FreeTypeFont | ImageFont.ImageFont, content_width: int, scale: float
    ) -> tuple[str, int, int]:
        """Wrap text and calculate dimensions.

        Args:
            text: Text to wrap
            font: Font for rendering
            content_width: Maximum text width
            scale: Proportional scale factor

        Returns:
            Tuple of (wrapped_text, text_width, text_height)
        """
        # Estimate character width for wrapping
        avg_char_width = self.text_size * scale * 0.6
        wrap_width = max(10, int(content_width / max(1, avg_char_width)))
        wrapped_text = textwrap.fill(text, width=wrap_width)

        # Calculate actual text dimensions
        temp_img = Image.new("RGB", (1, 1))
        temp_draw = ImageDraw.Draw(temp_img)
        text_bbox = temp_draw.textbbox((0, 0), wrapped_text, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]

        return wrapped_text, text_width, text_height

    def _calculate_qr_size(
        self,
        target_height: int,
        padding: int,
        logo_height: int,
        gap: int,
        text_height: int,
    ) -> int:
        """Calculate optimal QR code size to fit layout.

        Args:
            target_height: Total image height
            padding: Edge padding
            logo_height: Height of logo
            gap: Spacing between elements
            text_height: Height of text block

        Returns:
            QR code size (width and height, always square)
        """
        used_height = padding + logo_height + gap + gap + text_height + padding
        qr_max_height = max(1, target_height - used_height)
        return qr_max_height

    def _generate_qr_code(self, text: str, target_size: int) -> Image.Image:
        """Generate QR code at target size.

        Args:
            text: Text to encode
            target_size: Target QR code size (square)

        Returns:
            Square QR code image
        """
        # First pass: determine module count
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_M,
            box_size=1,
            border=QR_BORDER_SIZE,
        )
        qr.add_data(text)
        qr.make(fit=True)
        total_modules = qr.modules_count + 2 * qr.border

        # Second pass: generate at optimal box size
        box_size = max(1, target_size // total_modules)
        qr_final = qrcode.QRCode(
            version=qr.version,
            error_correction=qrcode.constants.ERROR_CORRECT_M,
            box_size=box_size,
            border=QR_BORDER_SIZE,
        )
        qr_final.add_data(text)
        qr_final.make(fit=True)
        qr_img = qr_final.make_image(fill_color="black", back_color="white").convert("RGB")

        # Resize to exact square target (NEAREST keeps edges sharp)
        if qr_img.size[0] != target_size:
            qr_img = qr_img.resize((target_size, target_size), Image.Resampling.NEAREST)

        return qr_img

    def _calc_x_position(
        self, align: AlignmentType, canvas_width: int, element_width: int, padding: int
    ) -> int:
        """Calculate horizontal position based on alignment.

        Args:
            align: Alignment type ("left", "center", "right")
            canvas_width: Total canvas width
            element_width: Width of element to position
            padding: Edge padding

        Returns:
            X coordinate for element placement
        """
        if align == "left":
            return padding
        elif align == "right":
            return canvas_width - element_width - padding
        else:  # center
            return (canvas_width - element_width) // 2

    def _compose_final_image(
        self,
        target_width: int,
        target_height: int,
        padding: int,
        gap: int,
        logo: Image.Image,
        qr_image: Image.Image,
        wrapped_text: str,
        text_width: int,
        font: ImageFont.FreeTypeFont | ImageFont.ImageFont,
    ) -> Image.Image:
        """Compose final image with all elements.

        Args:
            target_width: Output image width
            target_height: Output image height
            padding: Edge padding
            gap: Spacing between elements
            logo: Logo image
            qr_image: QR code image
            wrapped_text: Wrapped text string
            text_width: Text width
            font: Font for text rendering

        Returns:
            Final composed image
        """
        final_img = Image.new("RGB", (target_width, target_height), "white")

        # Position and paste logo at top
        logo_x = self._calc_x_position(self.logo_align, target_width, logo.width, padding)
        final_img.paste(logo, (logo_x, padding), logo)

        # Position and paste QR code below logo
        qr_x = self._calc_x_position(self.qr_align, target_width, qr_image.width, padding)
        qr_y = padding + logo.height + gap
        final_img.paste(qr_image, (qr_x, qr_y))

        # Draw text below QR code
        draw = ImageDraw.Draw(final_img)
        text_x = self._calc_x_position(self.text_align, target_width, text_width, padding)
        text_y = qr_y + qr_image.height + gap
        draw.text((text_x, text_y), wrapped_text, fill="black", font=font)

        return final_img
