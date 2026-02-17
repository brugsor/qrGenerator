# QR Generator Project Memory

## Project Structure
- **qr_gui.py**: Single-class tkinter app (QRGeneratorApp) with Windows-only clipboard support
- **qrGenerator.py**: CLI tool for basic QR code generation
- Default logo path: `sources\Prysmian_Logo_CMYK_Black.png`
- Output directory: `generatedQRs/`

## Key Architecture Patterns
- All rendering happens in `_build_qr_image(text, target_w, target_h)` which returns PIL Image
- Proportional scaling based on 1200x600 baseline (4"x2" at 300 DPI)
- User settings stored in tk.StringVar and tk.IntVar for reactivity
- Custom logo path stored in `self.custom_logo_path` (None = use default)

## UI Styling
- Modern color palette applied via ttk.Style configuration
- Button hierarchy: Primary (blue) > Accent (orange) > Secondary (slate) > Outline
- Background colors: Root (#F8FAFC), Frames (#FFFFFF)
- Custom styles: Primary.TButton, Accent.TButton, Secondary.TButton, Outline.TButton, Title.TLabel

## Windows-Specific
- Uses win32clipboard for BMP clipboard operations
- Requires pywin32 package
- Path strings with backslashes must use raw strings (r"path\to\file")

## Logo Upload Feature
- Custom logo path stored in instance variable, falls back to default
- `_get_logo_path()` helper returns active logo path
- Logo status displayed in UI with reset button
- Logo upload validates image is readable before accepting
