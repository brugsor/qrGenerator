# QR Generator - Architecture Documentation

This document describes the modular architecture of the QR code generator application.

## Project Structure

```
qrGenerator/
├── qr_gui.py              # GUI entry point (thin wrapper)
├── qrGenerator.py         # CLI entry point (thin wrapper)
├── requirements.txt       # Python dependencies
├── CLAUDE.md              # Project instructions for AI assistant
├── ARCHITECTURE.md        # This file
│
├── src/                   # Main application package
│   ├── __init__.py
│   ├── config.py          # Configuration constants
│   │
│   ├── core/              # Core business logic
│   │   ├── __init__.py
│   │   ├── qr_builder.py  # QR generation and image composition
│   │   └── file_ops.py    # File I/O and batch export
│   │
│   ├── ui/                # User interface components
│   │   ├── __init__.py
│   │   ├── app.py         # Main GUI application class
│   │   └── styles.py      # TTK styling configuration
│   │
│   └── utils/             # Utility modules
│       ├── __init__.py
│       ├── clipboard.py   # Windows clipboard operations
│       └── dimensions.py  # Unit conversion helpers
│
├── sources/               # Source assets and CLI output
│   └── Prysmian_Logo_CMYK_Black.png
│
└── generatedQRs/          # GUI output directory
```

## Module Descriptions

### Entry Points

#### `qr_gui.py`
- Launches the tkinter GUI application
- Imports and initializes `QRGeneratorApp` from `src.ui`
- Applies TTK styling via `configure_styles()`
- Keeps entry point minimal (thin wrapper pattern)

#### `qrGenerator.py`
- Command-line interface for basic QR generation
- Generates bare QR codes without logo/text composition
- Outputs to `sources/` directory
- Usage: `python qrGenerator.py <text1> <text2> ...`

### Configuration (`src/config.py`)

Centralizes all configuration constants:
- Directory paths (`OUTPUT_DIR`, `CLI_OUTPUT_DIR`, `DEFAULT_LOGO_PATH`)
- Output settings (`OUTPUT_DPI`, unit conversion constants)
- Default dimensions and design values
- Font mappings and limits
- QR code parameters

**Key principle**: All magic numbers and configuration live here, not scattered throughout the codebase.

### Core Business Logic (`src/core/`)

#### `qr_builder.py` - QRImageBuilder Class

The heart of QR code generation and image composition.

**Responsibilities:**
- Generate QR codes using the `qrcode` library
- Load and scale logos maintaining aspect ratio
- Render and wrap text with specified fonts
- Compose all elements (logo, QR, text) into final image
- Handle proportional scaling based on target dimensions

**Key Methods:**
- `__init__(logo_path, logo_align, qr_align, text_align, ...)` - Configure builder
- `build_image(text, target_width, target_height)` - Generate complete QR image
- Internal helpers for each component (logo, QR, text)

**Design Pattern**: Builder pattern with composition

#### `file_ops.py` - File Operations

Handles all file I/O operations.

**Functions:**
- `save_qr_image(image, filepath, dpi)` - Save single image with metadata
- `export_qr_codes_to_zip(texts, zip_path, image_builder, ...)` - Batch export with progress tracking

**Key Features:**
- Creates directories as needed
- Thread-safe for use with GUI progress dialogs
- Supports cancellation via callback
- Automatic cleanup on error

### User Interface (`src/ui/`)

#### `app.py` - QRGeneratorApp Class

Main GUI application class focusing exclusively on UI concerns.

**Responsibilities:**
- Build UI layout with tkinter/ttk
- Manage application state (current image, batch list, settings)
- Handle user events (button clicks, file dialogs)
- Delegate business logic to core modules
- Update preview display

**State Variables:**
- `current_qr_image`: Currently displayed PIL Image
- `strings_list`: Batch of texts to encode
- `current_index`: Position in batch
- `custom_logo_path`: User-uploaded logo (None = use default)
- Design settings stored in tk variables

**Key Methods:**
- `setup_ui()` - Build interface layout
- `generate_qr()` - Generate QR code(s) from input
- `save_qr()`, `copy_to_clipboard()` - Export operations
- `_export_all_zip()` - Batch export with progress dialog
- Navigation methods for batch mode

**Design Principle**: UI class does NOT contain business logic. It creates `QRImageBuilder` instances and calls their methods.

#### `styles.py` - TTK Styling

Configures visual appearance of the application.

**Function:**
- `configure_styles(root)` - Apply all TTK styles to root window

**Design Elements:**
- Modern color palette (blue, orange, slate)
- Button hierarchy: Primary > Accent > Secondary > Outline
- Consistent spacing and typography
- Focus states and hover effects

### Utilities (`src/utils/`)

#### `clipboard.py` - Windows Clipboard Operations

**Function:**
- `copy_image_to_clipboard(image)` - Copy PIL Image to Windows clipboard as BMP

**Platform Requirement**: Windows-only, requires `pywin32`

**Implementation Note**: Removes BMP file header before clipboard operation

#### `dimensions.py` - Unit Conversion

**Function:**
- `convert_to_pixels(width, height, unit)` - Convert cm/in/px to pixels at 300 DPI

**Supported Units:**
- `"cm"` - Centimeters
- `"in"` - Inches
- `"px"` - Pixels (direct)

**Returns**: Tuple of (width_pixels, height_pixels)

## Design Principles

### Separation of Concerns
- **UI layer** (`src/ui/`) handles user interaction and display
- **Business logic** (`src/core/`) handles QR generation and composition
- **Utilities** (`src/utils/`) provide cross-cutting functionality
- **Configuration** (`src/config.py`) centralizes all constants

### Dependency Direction
```
UI → Core ← Utils
 ↓     ↓
   Config
```

UI and Core both depend on Config. UI depends on Core. Utils are used by both UI and Core. Core never depends on UI.

### Type Safety
- All public functions have type hints
- Return types specified for clarity
- Type hints enable better IDE support and catch errors early

### Documentation
- Google-style docstrings for all public functions and classes
- Args, Returns, and Raises sections where applicable
- Module-level docstrings explain purpose

### Error Handling
- Specific exception types (ValueError, FileNotFoundError, OSError)
- User-friendly error messages
- Cleanup on failure (e.g., partial ZIP files)

### Testability
- Pure functions where possible (e.g., dimension conversion)
- Business logic separated from UI (easy to test without GUI)
- Dependency injection (e.g., image_builder callback in export_qr_codes_to_zip)

## Data Flow

### Single QR Generation (GUI)
1. User enters text and clicks "Generate QR Code"
2. `QRGeneratorApp.generate_qr()` called
3. Validates input, converts dimensions to pixels
4. Creates `QRImageBuilder` with current settings
5. Calls `builder.build_image(text, width, height)`
6. `QRImageBuilder` generates QR, loads logo, renders text, composes image
7. Returns PIL Image to UI
8. UI displays image in canvas and enables Save/Copy buttons

### Batch Export to ZIP
1. User clicks "Export All as ZIP"
2. UI validates inputs, creates progress dialog
3. Spawns background thread
4. Thread calls `export_qr_codes_to_zip()` with:
   - List of texts
   - ZIP path
   - Image builder function (closure over current settings)
   - Progress callback (updates UI on main thread)
   - Cancel flag (checks for user cancellation)
5. Export function generates each QR, writes to ZIP, reports progress
6. On completion/cancellation/error, updates UI accordingly

## Extending the Application

### Adding a New Output Format

1. Add new function to `src/core/file_ops.py`:
   ```python
   def save_qr_as_pdf(image: Image.Image, filepath: Path) -> None:
       # Implementation here
   ```

2. Add UI button in `src/ui/app.py`:
   ```python
   def save_as_pdf(self):
       filepath = filedialog.asksaveasfilename(...)
       save_qr_as_pdf(self.current_qr_image, Path(filepath))
   ```

### Adding a New Design Setting

1. Add constant to `src/config.py`:
   ```python
   DEFAULT_BORDER_COLOR = "#000000"
   ```

2. Add parameter to `QRImageBuilder.__init__()` in `src/core/qr_builder.py`

3. Use parameter in `build_image()` method

4. Add UI control in `src/ui/app.py._create_design_settings_section()`

5. Pass variable to `QRImageBuilder` in `_get_qr_builder()`

### Adding Cross-Platform Clipboard Support

1. Create platform detection in `src/utils/clipboard.py`:
   ```python
   import sys

   if sys.platform == "win32":
       from .clipboard_windows import copy_image_to_clipboard
   elif sys.platform == "darwin":
       from .clipboard_macos import copy_image_to_clipboard
   else:
       from .clipboard_linux import copy_image_to_clipboard
   ```

2. Implement platform-specific modules

## Code Quality Checklist

When adding new code, ensure:

- [ ] Type hints on all function signatures
- [ ] Docstrings with Args/Returns/Raises sections
- [ ] Imports organized: stdlib, third-party, local
- [ ] pathlib.Path used for file operations
- [ ] Constants defined in config.py (no magic numbers)
- [ ] Functions under 30 lines
- [ ] Specific exception types in error handling
- [ ] No UI logic in core modules
- [ ] No business logic in UI modules

## Running the Application

### GUI Mode
```bash
# Activate virtual environment first
source venv/Scripts/activate  # Unix
.\venv\Scripts\activate       # Windows

# Run GUI
python qr_gui.py
```

### CLI Mode
```bash
source venv/Scripts/activate

# Generate QR codes
python qrGenerator.py "Text 1" "Text 2" "Text 3"

# Output saved to sources/qr_1.png, sources/qr_2.png, etc.
```

### Installing Dependencies
```bash
pip install -r requirements.txt
```

## Dependencies

- **qrcode** - QR code generation
- **Pillow** - Image manipulation
- **pywin32** - Windows clipboard (Windows only)
- **colorama** - Terminal colors (optional)

## Platform Compatibility

- **GUI**: Windows only (due to clipboard operations)
- **CLI**: Cross-platform

To make GUI cross-platform, implement platform-specific clipboard modules as described in "Extending the Application" section.
