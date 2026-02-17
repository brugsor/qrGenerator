# QR Generator Project Memory

## Project Structure (Modular Architecture)
- **Entry points**: `qr_gui.py` (GUI), `qrGenerator.py` (CLI) - thin wrappers
- **Core package**: `src/` with clean separation of concerns
  - `src/config.py`: All constants and configuration values
  - `src/core/`: Business logic (QRImageBuilder, file operations)
  - `src/ui/`: UI-specific code (app class, TTK styling)
  - `src/utils/`: Cross-cutting utilities (clipboard, dimension conversion)
- Default logo: `sources\Prysmian_Logo_CMYK_Black.png`
- Output: `generatedQRs/` (GUI), `sources/` (CLI)

## Key Architecture Patterns
- **QRImageBuilder** (`src/core/qr_builder.py`): Core business logic
  - Constructor accepts all design parameters
  - `build_image(text, width, height)` returns PIL Image
  - Proportional scaling based on 1200x600 baseline (4"x2" @ 300 DPI)
- **File operations** (`src/core/file_ops.py`): save_qr_image(), export_qr_codes_to_zip()
- **Dimension conversion** (`src/utils/dimensions.py`): convert_to_pixels(w, h, unit)
- **Clipboard** (`src/utils/clipboard.py`): Windows-only, isolated
- **UI styling** (`src/ui/styles.py`): configure_styles() - all TTK styling
- **App class** (`src/ui/app.py`): UI logic only, delegates to core modules

## Code Quality Standards
- Type hints on all function signatures
- Docstrings (Google style) for all public functions/classes
- Import order: stdlib, third-party, local (PEP 8)
- pathlib.Path for all file operations (not os.path)
- Functions under 30 lines where possible
- Specific exception types in error handling

## UI Implementation
- TTK styling: Primary (blue), Accent (orange), Secondary (slate), Outline buttons
- User settings in tk variables for reactivity
- Custom logo path with fallback to default

## Windows-Specific
- Clipboard requires pywin32 (win32clipboard for BMP format)
- Always activate venv: `source venv/Scripts/activate`
