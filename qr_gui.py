"""QR Code Generator - GUI Entry Point

Launches the tkinter-based graphical user interface for QR code generation.

This module serves as the main entry point for the GUI application. All business
logic has been refactored into the src/ package for better modularity and
separation of concerns.
"""

import tkinter as tk

from src.ui import QRGeneratorApp, configure_styles


def main() -> None:
    """Initialize and run the QR code generator GUI application."""
    root = tk.Tk()
    configure_styles(root)
    app = QRGeneratorApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
