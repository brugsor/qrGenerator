"""TTK style configuration for the GUI.

This module defines the visual appearance of the application using
ttk.Style with a modern color palette.
"""

import tkinter as tk
from tkinter import ttk


# Modern color palette
PRIMARY_COLOR = "#2563EB"  # Blue 600
PRIMARY_HOVER = "#1E40AF"  # Blue 700
PRIMARY_PRESSED = "#1E3A8A"  # Blue 800
SECONDARY_COLOR = "#64748B"  # Slate 500
SECONDARY_HOVER = "#475569"  # Slate 600
SECONDARY_PRESSED = "#334155"  # Slate 700
ACCENT_COLOR = "#F97316"  # Orange 500
ACCENT_HOVER = "#EA580C"  # Orange 600
ACCENT_PRESSED = "#C2410C"  # Orange 700
BG_COLOR = "#F8FAFC"  # Slate 50
FRAME_BG = "#FFFFFF"  # White
BORDER_COLOR = "#E2E8F0"  # Slate 200
TEXT_COLOR = "#1E293B"  # Slate 800
TEXT_DISABLED = "#94A3B8"  # Slate 400


def configure_styles(root: tk.Tk) -> None:
    """Configure ttk styles for the application.

    Args:
        root: Root tkinter window
    """
    style = ttk.Style()
    style.theme_use("clam")

    # Configure root window background
    root.configure(bg=BG_COLOR)

    # Primary button style (for main actions like Generate)
    style.configure(
        "Primary.TButton",
        background=PRIMARY_COLOR,
        foreground="white",
        borderwidth=0,
        focuscolor="none",
        font=("Segoe UI", 9, "bold"),
        padding=(12, 6),
        relief="flat",
    )
    style.map(
        "Primary.TButton",
        background=[
            ("disabled", "#CBD5E1"),  # Slate 300
            ("pressed", PRIMARY_PRESSED),
            ("active", PRIMARY_HOVER),
        ],
        foreground=[
            ("disabled", TEXT_DISABLED),
            ("pressed", "white"),
            ("active", "white"),
            ("!disabled", "white"),
        ],
    )

    # Accent button style (for special actions like Save)
    style.configure(
        "Accent.TButton",
        background=ACCENT_COLOR,
        foreground="white",
        borderwidth=0,
        focuscolor="none",
        font=("Segoe UI", 9, "bold"),
        padding=(12, 6),
        relief="flat",
    )
    style.map(
        "Accent.TButton",
        background=[
            ("disabled", "#CBD5E1"),  # Slate 300
            ("pressed", ACCENT_PRESSED),
            ("active", ACCENT_HOVER),
        ],
        foreground=[
            ("disabled", TEXT_DISABLED),
            ("pressed", "white"),
            ("active", "white"),
            ("!disabled", "white"),
        ],
    )

    # Secondary button style (for less prominent actions)
    style.configure(
        "Secondary.TButton",
        background=SECONDARY_COLOR,
        foreground="white",
        borderwidth=0,
        focuscolor="none",
        font=("Segoe UI", 9),
        padding=(10, 5),
        relief="flat",
    )
    style.map(
        "Secondary.TButton",
        background=[
            ("disabled", "#CBD5E1"),  # Slate 300
            ("pressed", SECONDARY_PRESSED),
            ("active", SECONDARY_HOVER),
        ],
        foreground=[
            ("disabled", TEXT_DISABLED),
            ("pressed", "white"),
            ("active", "white"),
            ("!disabled", "white"),
        ],
    )

    # Outline button style (for tertiary actions)
    style.configure(
        "Outline.TButton",
        background=FRAME_BG,
        foreground=TEXT_COLOR,
        borderwidth=1,
        bordercolor=BORDER_COLOR,
        focuscolor="none",
        font=("Segoe UI", 9),
        padding=(10, 5),
        relief="solid",
    )
    style.map(
        "Outline.TButton",
        background=[
            ("disabled", "#F1F5F9"),  # Slate 100
            ("pressed", "#E2E8F0"),  # Slate 200
            ("active", BG_COLOR),
        ],
        foreground=[
            ("disabled", TEXT_DISABLED),
            ("pressed", TEXT_COLOR),
            ("active", TEXT_COLOR),
            ("!disabled", TEXT_COLOR),
        ],
        bordercolor=[
            ("disabled", "#CBD5E1"),  # Slate 300
            ("active", BORDER_COLOR),
        ],
    )

    # Frame styles
    style.configure("TFrame", background=FRAME_BG)
    style.configure("Card.TFrame", background=FRAME_BG, relief="flat", borderwidth=1)

    # LabelFrame style
    style.configure(
        "TLabelframe",
        background=FRAME_BG,
        borderwidth=1,
        relief="solid",
        bordercolor=BORDER_COLOR,
    )
    style.configure(
        "TLabelframe.Label",
        background=FRAME_BG,
        foreground=TEXT_COLOR,
        font=("Segoe UI", 9, "bold"),
    )

    # Label styles
    style.configure(
        "TLabel", background=FRAME_BG, foreground=TEXT_COLOR, font=("Segoe UI", 9)
    )
    style.configure(
        "Title.TLabel",
        background=FRAME_BG,
        foreground=TEXT_COLOR,
        font=("Segoe UI", 18, "bold"),
    )

    # Entry style
    style.configure(
        "TEntry",
        fieldbackground="white",
        foreground=TEXT_COLOR,
        borderwidth=1,
        bordercolor=BORDER_COLOR,
        insertcolor=PRIMARY_COLOR,
        relief="solid",
    )
    style.map(
        "TEntry",
        fieldbackground=[("disabled", "#F1F5F9")],
        foreground=[("disabled", TEXT_DISABLED)],
        bordercolor=[("focus", PRIMARY_COLOR), ("!focus", BORDER_COLOR)],
    )

    # Combobox style
    style.configure(
        "TCombobox",
        fieldbackground="white",
        background="white",
        foreground=TEXT_COLOR,
        borderwidth=1,
        bordercolor=BORDER_COLOR,
        arrowcolor=TEXT_COLOR,
        relief="solid",
    )
    style.map(
        "TCombobox",
        fieldbackground=[("readonly", "white"), ("disabled", "#F1F5F9")],
        foreground=[("disabled", TEXT_DISABLED)],
        bordercolor=[("focus", PRIMARY_COLOR), ("!focus", BORDER_COLOR)],
        arrowcolor=[("disabled", TEXT_DISABLED)],
    )

    # Radiobutton style
    style.configure(
        "TRadiobutton",
        background=FRAME_BG,
        foreground=TEXT_COLOR,
        font=("Segoe UI", 9),
    )
    style.map(
        "TRadiobutton",
        background=[("active", FRAME_BG)],
        foreground=[("disabled", TEXT_DISABLED)],
    )

    # Progressbar style
    style.configure(
        "TProgressbar",
        background=PRIMARY_COLOR,
        troughcolor=BORDER_COLOR,
        borderwidth=0,
        relief="flat",
    )
