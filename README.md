# QR Code Generator

A Python-based QR code generator with both a command-line interface (CLI) for batch generation and a graphical user interface (GUI) with logo branding, preview, and clipboard support.

## Features

### CLI (`qrGenerator.py`)
- Batch QR code generation from multiple input strings
- Saves output to the `sources/` directory

### GUI (`qr_gui.py`)
- Interactive QR code generation with real-time preview
- Logo branding — automatically embeds the nosGolearon logo above the QR code
- Encoded text displayed below the QR code with automatic word wrapping
- Save as PNG or JPEG
- Copy to Windows clipboard
- Keyboard shortcut: `Ctrl+Enter` to generate

## Requirements

- Python 3.9+
- Windows (required for clipboard functionality in the GUI)

## Installation

```bash
# Clone the repository
git clone https://github.com/<your-username>/qrGenerator.git
cd qrGenerator

# Create and activate a virtual environment
python -m venv venv
.\venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Dependencies

| Package | Purpose |
|---------|---------|
| `qrcode[pil]` | QR code generation |
| `Pillow` | Image processing |
| `pywin32` | Windows clipboard access (GUI only) |

## Usage

### CLI

```bash
python qrGenerator.py "Text 1" "https://example.com" "Hello World"
```

Generates one QR code per argument, saved as `sources/qr_1.png`, `sources/qr_2.png`, etc.

### GUI

```bash
python qr_gui.py
```

1. Enter text in the input field.
2. Click **Generate QR Code** (or press `Ctrl+Enter`).
3. Preview the result in the canvas.
4. **Save QR Code** — choose a filename and format (PNG/JPEG).
5. **Copy to Clipboard** — copies the image to the Windows clipboard.
6. **Clear** — resets the input and preview.

## Project Structure

```
qrGenerator/
├── qrGenerator.py          # CLI batch QR code generator
├── qr_gui.py               # GUI QR code generator
├── requirements.txt        # Python dependencies
├── sources/                # Logo asset & CLI output directory
│   └── nosGolearon_logo_1000x250px.png
├── generatedQRs/           # GUI output directory
└── README.md
```

## QR Code Settings

| Setting | Value |
|---------|-------|
| Version | 1 (auto-fit) |
| Error Correction | Medium (~15% recovery) |
| Box Size | 10 px |
| Border | 4 modules |

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.
